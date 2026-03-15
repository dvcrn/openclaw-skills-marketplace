#!/usr/bin/env python3
"""pipeline.py - Main entry point for doc-reader.

Orchestrates: pre-check → converter → chunker → enricher → assembler.
Manages state for crash recovery via state.json.

Usage:
  python3 scripts/pipeline.py <input_file> --output <output_dir> \
    [--mode archive-only|archive+index|archive+index+insights] \
    [--split-by year|topic|chapter|none]
"""

import argparse
import hashlib
import json
import os
import sys
import time

# Resolve script directory for sibling imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

import converter
import chunker
import enricher as enricher_mod
import assembler


# Steps in order
STEPS = ["convert", "chunk", "enrich", "assemble"]

SUPPORTED_FORMATS = {".docx", ".pdf", ".txt", ".text", ".md", ".markdown"}


def compute_file_hash(path):
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            block = f.read(65536)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def generate_job_id():
    """Generate a job ID based on timestamp."""
    return time.strftime("%Y%m%d-%H%M%S")


def load_state(output_dir):
    """Load state.json if it exists."""
    state_path = os.path.join(output_dir, "state.json")
    if os.path.exists(state_path):
        with open(state_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_state(output_dir, state):
    """Persist state to state.json."""
    state_path = os.path.join(output_dir, "state.json")
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def detect_mode(requested_mode):
    """Auto-select mode based on env vars and requested mode."""
    api_key = os.environ.get("DOC_READER_API_KEY", "")
    allow_external = os.environ.get("DOC_READER_ALLOW_EXTERNAL", "false").lower()

    if requested_mode == "archive+index+insights":
        if not api_key:
            print("[pipeline] WARNING: No DOC_READER_API_KEY set. Downgrading to archive+index.")
            return "archive+index"
        if allow_external == "false":
            print("[pipeline] WARNING: DOC_READER_ALLOW_EXTERNAL=false. Downgrading to archive+index.")
            print("  Set DOC_READER_ALLOW_EXTERNAL=true to enable LLM enrichment.")
            return "archive+index"
        return "archive+index+insights"

    if requested_mode:
        return requested_mode

    # Auto-detect
    if api_key and allow_external == "true":
        return "archive+index+insights"
    elif api_key:
        return "archive+index"
    else:
        return "archive-only"


def pre_check(input_path):
    """Validate input file and gather metadata."""
    if not os.path.exists(input_path):
        print(f"ERROR: File not found: {input_path}")
        sys.exit(1)

    ext = os.path.splitext(input_path)[1].lower()
    if ext not in SUPPORTED_FORMATS:
        print(f"ERROR: Unsupported format '{ext}'.")
        print(f"Supported: {', '.join(sorted(SUPPORTED_FORMATS))}")
        sys.exit(1)

    file_size = os.path.getsize(input_path)
    if file_size == 0:
        print("WARNING: Input file is empty (0 bytes)")

    # Estimate page count (rough: 2500 chars/page for text, or file size based)
    est_pages = max(1, file_size // 2500) if ext in (".txt", ".md", ".markdown") else max(1, file_size // 5000)

    print(f"[pipeline] Input: {os.path.basename(input_path)}")
    print(f"[pipeline] Format: {ext}, Size: {file_size:,} bytes, Est. pages: ~{est_pages}")

    return {
        "format": ext,
        "file_size": file_size,
        "est_pages": est_pages,
    }


def run_pipeline(input_path, output_dir, mode, split_by):
    """Run the full pipeline with state management."""
    os.makedirs(output_dir, exist_ok=True)

    # Pre-check
    meta = pre_check(input_path)
    source_hash = compute_file_hash(input_path)

    # Check for existing state (resume support)
    state = load_state(output_dir)
    if state and state.get("source_hash") == source_hash:
        print(f"[pipeline] Resuming job {state['job_id']} from step: {state.get('last_completed', 'none')}")
    else:
        if state:
            print("[pipeline] Source file changed, starting fresh")
        state = {
            "job_id": generate_job_id(),
            "source_path": os.path.abspath(input_path),
            "source_hash": source_hash,
            "mode": mode,
            "split_by": split_by,
            "last_completed": None,
            "warnings": [],
            "failed_chunks": [],
            "status": "running",
        }
        save_state(output_dir, state)

    print(f"[pipeline] Job: {state['job_id']}, Mode: {mode}")
    print()

    # Define file paths
    md_path = os.path.join(output_dir, "converted.md")
    chunks_path = os.path.join(output_dir, "chunks.jsonl")
    enriched_path = os.path.join(output_dir, "enriched_chunks.jsonl")

    last_done = state.get("last_completed")
    steps_done = STEPS[:STEPS.index(last_done) + 1] if last_done and last_done in STEPS else []

    # Step 1: Convert
    if "convert" not in steps_done:
        print("=" * 50)
        print("STEP 1/4: Converting to Markdown")
        print("=" * 50)
        warnings = converter.convert(input_path, md_path)
        state["warnings"].extend(warnings)
        state["last_completed"] = "convert"
        save_state(output_dir, state)
        print()

    # Step 2: Chunk
    if "chunk" not in steps_done:
        print("=" * 50)
        print("STEP 2/4: Splitting into chunks")
        print("=" * 50)
        with open(md_path, "r", encoding="utf-8") as f:
            text = f.read()
        chunks = chunker.chunk_text(text)
        with open(chunks_path, "w", encoding="utf-8") as f:
            for ch in chunks:
                f.write(json.dumps(ch, ensure_ascii=False) + "\n")
        print(f"[pipeline] {len(chunks)} chunks generated")
        state["chunk_count"] = len(chunks)
        state["last_completed"] = "chunk"
        save_state(output_dir, state)
        print()

    # Step 3: Enrich (only in insights mode)
    if "enrich" not in steps_done:
        if mode == "archive+index+insights":
            print("=" * 50)
            print("STEP 3/4: LLM Enrichment")
            print("=" * 50)
            try:
                failed = enricher_mod.enrich(chunks_path, enriched_path)
                state["failed_chunks"] = failed
            except SystemExit:
                print("[pipeline] Enrichment failed. Continuing without enrichment.")
                state["warnings"].append("Enrichment failed, downgraded to archive+index")
                mode = "archive+index"
                state["mode"] = mode
            except Exception as e:
                print(f"[pipeline] Enrichment error: {e}. Continuing without enrichment.")
                state["warnings"].append(f"Enrichment error: {e}")
                mode = "archive+index"
                state["mode"] = mode
        else:
            print("STEP 3/4: Enrichment skipped (mode: {})".format(mode))

        state["last_completed"] = "enrich"
        save_state(output_dir, state)
        print()

    # Step 4: Assemble
    if "assemble" not in steps_done:
        print("=" * 50)
        print("STEP 4/4: Assembling output")
        print("=" * 50)

        # Use enriched chunks if available, else plain chunks
        final_chunks_path = enriched_path if os.path.exists(enriched_path) else chunks_path

        outputs = assembler.assemble(
            final_chunks_path, output_dir, split_by,
            warnings=state.get("warnings"),
            failed_chunks=state.get("failed_chunks"),
            mode=mode,
        )

        state["last_completed"] = "assemble"
        state["outputs"] = outputs
        save_state(output_dir, state)
        print()

    # Generate manifest.json
    manifest = {
        "job_id": state["job_id"],
        "source_path": state["source_path"],
        "source_hash": state["source_hash"],
        "mode": mode,
        "converter": "pandoc" if meta["format"] == ".docx" else ("pdftotext" if meta["format"] == ".pdf" else "direct"),
        "chunk_count": state.get("chunk_count", 0),
        "status": "completed_with_warnings" if state.get("warnings") or state.get("failed_chunks") else "completed",
        "warnings": state.get("warnings", []),
        "outputs": state.get("outputs", []),
    }

    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    state["status"] = manifest["status"]
    save_state(output_dir, state)

    # Clean up intermediate file
    if os.path.exists(md_path):
        pass  # Keep converted.md for debugging; user can delete

    # Summary
    print("=" * 50)
    print("COMPLETE")
    print("=" * 50)
    print(f"Job ID:    {state['job_id']}")
    print(f"Mode:      {mode}")
    print(f"Chunks:    {state.get('chunk_count', '?')}")
    print(f"Status:    {manifest['status']}")
    print(f"Output:    {output_dir}")
    if manifest["warnings"]:
        print(f"Warnings:  {len(manifest['warnings'])}")
    print(f"\nFiles generated:")
    for f_name in state.get("outputs", []):
        print(f"  - {f_name}")
    print(f"  - manifest.json")
    print(f"  - chunks.jsonl")

    return manifest


def main():
    parser = argparse.ArgumentParser(
        description="doc-reader pipeline: convert, chunk, enrich, and assemble documents.",
    )
    parser.add_argument("input_file", help="Path to input document")
    parser.add_argument("--output", "-o", required=True, help="Output directory")
    parser.add_argument(
        "--mode", "-m",
        choices=["archive-only", "archive+index", "archive+index+insights"],
        default=None,
        help="Processing mode (auto-detected if not specified)",
    )
    parser.add_argument(
        "--split-by",
        choices=["year", "topic", "chapter", "none"],
        default="none",
        help="Split output into parts by this dimension",
    )

    args = parser.parse_args()

    mode = detect_mode(args.mode)
    run_pipeline(args.input_file, args.output, mode, args.split_by)


if __name__ == "__main__":
    main()
