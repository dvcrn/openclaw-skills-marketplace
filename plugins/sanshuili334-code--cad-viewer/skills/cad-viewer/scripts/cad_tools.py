

def cmd_distance(args):
    doc = _load_dwg(args.file)
    msp = doc.modelspace()
    
    def _get_center(entity):
        etype = entity.dxftype()
        if etype == "INSERT":
            return (entity.dxf.insert.x, entity.dxf.insert.y, entity.dxf.insert.z)
        elif etype == "LINE":
            return ((entity.dxf.start.x + entity.dxf.end.x) / 2, (entity.dxf.start.y + entity.dxf.end.y) / 2, 0)
        elif etype in ("CIRCLE", "ARC"):
            return (entity.dxf.center.x, entity.dxf.center.y, entity.dxf.center.z)
        elif etype in ("TEXT", "MTEXT") and hasattr(entity.dxf, 'insert'):
            return (entity.dxf.insert.x, entity.dxf.insert.y, 0)
        elif etype == "LWPOLYLINE":
            pts = entity.get_points("xy")
            if pts:
                return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts), 0)
        return None
    
    def _find_pos(identifier):
        try:
            entity = doc.entitydb.get(identifier)
            if entity:
                return _get_center(entity)
        except:
            pass
        for entity in msp.query("INSERT"):
            if entity.dxf.name == identifier:
                return (entity.dxf.insert.x, entity.dxf.insert.y, entity.dxf.insert.z)
        return None
    
    if args.coord1:
        pos1 = tuple([float(x) for x in args.coord1.split(",")] + [0] * (3 - len(args.coord1.split(","))))
    else:
        pos1 = _find_pos(args.entity1)
    
    if args.coord2:
        pos2 = tuple([float(x) for x in args.coord2.split(",")] + [0] * (3 - len(args.coord2.split(","))))
    else:
        pos2 = _find_pos(args.entity2)
    
    if pos1 is None or pos2 is None:
        print(json.dumps({"status": "error", "message": "Could not find one or both entities/coordinates"}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
    
    dx, dy, dz = pos2[0] - pos1[0], pos2[1] - pos1[1], (pos2[2] - pos1[2]) if len(pos1) > 2 and len(pos2) > 2 else 0
    print(json.dumps({
        "point1": {"x": round(pos1[0], 4), "y": round(pos1[1], 4), "z": round(pos1[2], 4) if len(pos1) > 2 else 0},
        "point2": {"x": round(pos2[0], 4), "y": round(pos2[1], 4), "z": round(pos2[2], 4) if len(pos2) > 2 else 0},
        "distance_2d": round(math.hypot(dx, dy), 4),
        "distance_3d": round(math.sqrt(dx**2 + dy**2 + dz**2), 4),
        "delta_x": round(dx, 4), "delta_y": round(dy, 4), "delta_z": round(dz, 4),
        "unit": _get_unit_name(doc)
    }, ensure_ascii=False, indent=2))


def cmd_screenshot(args):
    doc = _load_dwg(args.file)
    msp = doc.modelspace()
    abs_dwg = os.path.abspath(args.file)
    start_x = start_y = width = height = None
    
    if args.region:
        parts = [float(x) for x in args.region.split(",")]
        if len(parts) != 4:
            print(json.dumps({"status": "error", "message": "--region format should be 'x,y,w,h'"}, ensure_ascii=False), file=sys.stderr)
            sys.exit(1)
        start_x, start_y, width, height = parts
    elif args.block_name:
        for entity in msp.query("INSERT"):
            if entity.dxf.name == args.block_name:
                r = args.radius or 5000
                start_x, start_y = entity.dxf.insert.x - r, entity.dxf.insert.y - r
                width = height = r * 2
                break
        if start_x is None:
            print(json.dumps({"status": "error", "message": f"Block '{args.block_name}' not found"}, ensure_ascii=False), file=sys.stderr)
            sys.exit(1)
    elif args.handle:
        try:
            entity = doc.entitydb.get(args.handle)
            if entity and entity.dxftype() == "INSERT":
                r = args.radius or 5000
                start_x, start_y = entity.dxf.insert.x - r, entity.dxf.insert.y - r
                width = height = r * 2
        except:
            print(json.dumps({"status": "error", "message": f"Handle '{args.handle}' not found"}, ensure_ascii=False), file=sys.stderr)
            sys.exit(1)
    elif args.layer_name:
        entities = msp.query(f'*[layer=="{args.layer_name}"]')
        if not entities:
            print(json.dumps({"status": "error", "message": f"No entities on layer '{args.layer_name}'"}, ensure_ascii=False), file=sys.stderr)
            sys.exit(1)
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        for e in entities:
            try:
                if e.dxftype() == "INSERT":
                    min_x, min_y = min(min_x, e.dxf.insert.x), min(min_y, e.dxf.insert.y)
                    max_x, max_y = max(max_x, e.dxf.insert.x), max(max_y, e.dxf.insert.y)
                elif e.dxftype() == "LINE":
                    for pt in (e.dxf.start, e.dxf.end):
                        min_x, min_y = min(min_x, pt.x), min(min_y, pt.y)
                        max_x, max_y = max(max_x, pt.x), max(max_y, pt.y)
                elif e.dxftype() in ("CIRCLE", "ARC"):
                    min_x, min_y = min(min_x, e.dxf.center.x - e.dxf.radius), min(min_y, e.dxf.center.y - e.dxf.radius)
                    max_x, max_y = max(max_x, e.dxf.center.x + e.dxf.radius), max(max_y, e.dxf.center.y + e.dxf.radius)
            except:
                continue
        p = args.radius or 2000
        start_x, start_y = min_x - p, min_y - p
        width, height = (max_x - min_x) + p * 2, (max_y - min_y) + p * 2
    
    output_path = os.path.abspath(args.output or "cad_screenshot.png")
    pixel_size = args.pixel_size or 3000
    qcad_tool = _find_qcad_tool(args.qcad_path)
    
    if qcad_tool:
        _screenshot_qcad(abs_dwg, output_path, qcad_tool, start_x, start_y, width, height, pixel_size, args.background or "black")
    else:
        _screenshot_matplotlib(doc, output_path, start_x, start_y, width, height, pixel_size)


def _screenshot_qcad(dwg_path, output_path, qcad_tool, start_x, start_y, width, height, pixel_size, background):
    cmd = ["xvfb-run", "-a", qcad_tool, "-f", "-b", background, "-a", "-c", "-q", "100"]
    if start_x is not None:
        cmd.extend(["-w", f"{start_x},{start_y},{width},{height}"])
    cmd.extend(["-width", str(pixel_size), "-height", str(pixel_size), "-o", output_path, dwg_path])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if os.path.exists(output_path):
            print(json.dumps({"status": "success", "output": output_path, "file_size_kb": round(os.path.getsize(output_path) / 1024, 1), "resolution": f"{pixel_size}x{pixel_size}", "method": "qcad"}, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({"status": "error", "message": f"Screenshot failed: {result.stderr}"}, ensure_ascii=False), file=sys.stderr)
            sys.exit(1)
    except subprocess.TimeoutExpired:
        print(json.dumps({"status": "error", "message": "Screenshot timeout (120s)"}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


def _screenshot_matplotlib(doc, output_path, start_x, start_y, width, height, pixel_size):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from ezdxf.addons.drawing import RenderContext, Frontend
        from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    except ImportError:
        print(json.dumps({"status": "error", "message": "matplotlib not installed. Run: pip install matplotlib"}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
    
    msp = doc.modelspace()
    fig = plt.figure(figsize=(pixel_size / 100, pixel_size / 100))
    ax = fig.add_axes([0, 0, 1, 1])
    ctx = RenderContext(doc)
    out = MatplotlibBackend(ax)
    out.set_background("#FFFFFF")
    Frontend(ctx, out).draw_layout(msp, finalize=True)
    if start_x is not None:
        ax.set_xlim(start_x, start_x + width)
        ax.set_ylim(start_y, start_y + height)
    ext = os.path.splitext(output_path)[1].lower()
    fmt = {"pdf": "pdf", "svg": "svg"}.get(ext, "png")
    fig.savefig(output_path, format=fmt, dpi=100)
    plt.close(fig)
    print(json.dumps({"status": "success", "output": output_path, "file_size_kb": round(os.path.getsize(output_path) / 1024, 1), "method": "matplotlib"}, ensure_ascii=False, indent=2))


def cmd_audit(args):
    doc = _load_dwg(args.file)
    msp = doc.modelspace()
    issues = []
    
    for entity in msp.query("INSERT"):
        if entity.dxf.layer == "0":
            issues.append({"severity": "error", "rule": "zero_layer_insert", "message": f"Block '{entity.dxf.name}' on default layer 0", "handle": entity.dxf.handle})
    
    seen_blocks = set()
    for entity in msp.query("INSERT"):
        name = entity.dxf.name
        if name in seen_blocks:
            continue
        seen_blocks.add(name)
        block_def = doc.blocks.get(name)
        if block_def:
            layers = set(e.dxf.layer for e in block_def)
            if "0" not in layers or len(layers) > 1:
                issues.append({"severity": "warning", "rule": "block_layer_mixed", "message": f"Block '{name}' uses multiple internal layers: {list(layers)}"})
    
    for layer in doc.layers:
        name = layer.dxf.name
        if name.startswith("*"):
            continue
        if not msp.query(f'*[layer=="{name}"]'):
            issues.append({"severity": "info", "rule": "empty_layer", "message": f"Layer '{name}' has no entities"})
    
    defpoints = msp.query('*[layer=="DEFPOINTS"]')
    if defpoints:
        issues.append({"severity": "warning", "rule": "defpoints_entities", "message": f"Found {len(defpoints)} entities on DEFPOINTS layer"})
    
    print(json.dumps({
        "total_issues": len(issues),
        "errors": len([i for i in issues if i["severity"] == "error"]),
        "warnings": len([i for i in issues if i["severity"] == "warning"]),
        "info": len([i for i in issues if i["severity"] == "info"]),
        "issues": issues
    }, ensure_ascii=False, indent=2))


def cmd_search(args):
    doc = _load_dwg(args.file)
    msp = doc.modelspace()
    keyword = args.keyword.lower()
    results = []
    
    for entity in msp:
        matched = False
        reason = ""
        etype = entity.dxftype()
        if etype == "INSERT" and keyword in entity.dxf.name.lower():
            matched, reason = True, f"Block name: '{entity.dxf.name}'"
        elif etype == "TEXT" and keyword in entity.dxf.text.lower():
            matched, reason = True, f"Text: '{entity.dxf.text}'"
        elif etype == "MTEXT" and keyword in entity.text.lower():
            matched, reason = True, f"MText: '{entity.text[:80]}'"
        elif keyword in entity.dxf.layer.lower():
            matched, reason = True, f"Layer: '{entity.dxf.layer}'"
        
        if matched:
            result = _entity_to_dict(entity)
            result["match_reason"] = reason
            results.append(result)
    
    limit = args.limit or len(results)
    print(json.dumps({"keyword": args.keyword, "total_matches": len(results), "returned": min(limit, len(results)), "results": results[:limit]}, ensure_ascii=False, indent=2))


def cmd_export_pdf(args):
    doc = _load_dwg(args.file)
    output_path = os.path.abspath(args.output or "cad_export.pdf")
    
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from ezdxf.addons.drawing import RenderContext, Frontend
        from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    except ImportError:
        print(json.dumps({"status": "error", "message": "matplotlib not installed. Run: pip install matplotlib"}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
    
    msp = doc.modelspace()
    fig = plt.figure(figsize=(16, 9))
    ax = fig.add_axes([0, 0, 1, 1])
    ctx = RenderContext(doc)
    out = MatplotlibBackend(ax)
    out.set_background(args.background or "#FFFFFF")
    Frontend(ctx, out).draw_layout(msp, finalize=True)
    fig.savefig(output_path, format="pdf")
    plt.close(fig)
    print(json.dumps({"status": "success", "output": output_path, "file_size_kb": round(os.path.getsize(output_path) / 1024, 1)}, ensure_ascii=False, indent=2))


def cmd_check_env(args):
    status = {}
    for pkg in ("ezdxf", "matplotlib"):
        try:
            mod = __import__(pkg)
            status[pkg] = {"installed": True, "version": getattr(mod, "__version__", "unknown")}
        except ImportError:
            status[pkg] = {"installed": False}
    
    status["xvfb"] = {"installed": subprocess.run(["which", "xvfb-run"], capture_output=True).returncode == 0}
    
    oda = _find_oda_wrapper()
    status["oda_file_converter"] = {"installed": oda is not None, "path": oda, "capability": "Read DWG files"}
    
    qcad = _find_qcad_tool()
    status["qcad_dwg2bmp"] = {"installed": qcad is not None, "path": qcad, "capability": "High-quality screenshots"}
    
    all_ok = all([status["ezdxf"]["installed"], status["matplotlib"]["installed"], status["oda_file_converter"]["installed"]])
    
    output = {"environment_ready": all_ok, "dependencies": status}
    if not all_ok:
        missing = []
        if not status["oda_file_converter"]["installed"]:
            missing.append("ODA File Converter (for DWG reading)")
        if not status["qcad_dwg2bmp"]["installed"]:
            missing.append("QCAD dwg2bmp (optional, for screenshots)")
        output["missing"] = missing
        output["fix_command"] = f"python3 {os.path.join(SCRIPT_DIR, 'cad_tools.py')} setup --confirm"
    
    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_setup(args):
    """Run environment setup with explicit user confirmation"""
    setup_script = os.path.join(SCRIPT_DIR, "setup.sh")
    if not os.path.exists(setup_script):
        print(json.dumps({"status": "error", "message": "setup.sh not found"}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
    
    # Require explicit confirmation
    if not args.confirm and not args.oda_rpm and not args.qcad_tar:
        print(json.dumps({
            "status": "confirmation_required",
            "message": "Setup requires explicit confirmation to download and install dependencies.",
            "actions": [
                "Run with --confirm to proceed with automatic setup",
                "Run with --oda-rpm and --qcad-tar to use local packages",
                "Install dependencies manually (see SKILL.md)"
            ],
            "warning": "Automatic setup will download from opendesign.com and qcad.org, and may use sudo for system packages."
        }, ensure_ascii=False, indent=2))
        sys.exit(1)
    
    cmd = ["bash", setup_script]
    if args.skip_oda:
        cmd.append("--skip-oda")
    if args.skip_qcad:
        cmd.append("--skip-qcad")
    if args.oda_rpm:
        cmd.extend(["--oda-rpm", args.oda_rpm])
    if args.qcad_tar:
        cmd.extend(["--qcad-tar", args.qcad_tar])
    
    result = subprocess.run(cmd, cwd=SCRIPT_DIR)
    sys.exit(result.returncode)


# ==================== Main Entry Point ====================

def main():
    parser = argparse.ArgumentParser(description="CAD DWG/DXF Drawing Professional Analysis Toolkit", formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")
    
    # info
    p = subparsers.add_parser("info", help="Get drawing basic information")
    p.add_argument("file", help="DWG/DXF file path")
    
    # layers
    p = subparsers.add_parser("layers", help="List all layers")
    p.add_argument("file", help="DWG/DXF file path")
    p.add_argument("--count-entities", action="store_true", help="Count entities on each layer")
    p.add_argument("--sort-by", choices=["name", "color"], default="name", help="Sort method")
    
    # entities
    p = subparsers.add_parser("entities", help="List model space entities")
    p.add_argument("file", help="DWG/DXF file path")
    p.add_argument("--type", help="Filter by type (INSERT/LINE/CIRCLE/TEXT/MTEXT/LWPOLYLINE)")
    p.add_argument("--layer", help="Filter by layer")
    p.add_argument("--limit", type=int, help="Limit results")
    
    # blocks
    p = subparsers.add_parser("blocks", help="List block definitions")
    p.add_argument("file", help="DWG/DXF file path")
    p.add_argument("--name-filter", help="Filter by name (fuzzy match)")
    
    # inserts
    p = subparsers.add_parser("inserts", help="List block reference instances")
    p.add_argument("file", help="DWG/DXF file path")
    p.add_argument("--name-filter", help="Filter by block name")
    p.add_argument("--analyze-layers", action="store_true", help="Analyze internal layer distribution")
    p.add_argument("--limit", type=int, help="Limit results")
    
    # texts
    p = subparsers.add_parser("texts", help="Extract all text from drawing")
    p.add_argument("file", help="DWG/DXF file path")
    p.add_argument("--keyword", help="Filter by keyword")
    p.add_argument("--limit", type=int, help="Limit results")
    
    # layer-content
    p = subparsers.add_parser("layer-content", help="Extract entity details on specified layer")
    p.add_argument("file", help="DWG/DXF file path")
    p.add_argument("layer_name", help="Target layer name")
    p.add_argument("--limit", type=int, help="Limit results")
    
    # spaces
    p = subparsers.add_parser("spaces", help="View space layout system")
    p.add_argument("file", help="DWG/DXF file path")
    p.add_argument("--detail", action="store_true", help="Show detailed layout information")
    
    # distance
    p = subparsers.add_parser("distance", help="Calculate distance between two points/entities")
    p.add_argument("file", help="DWG/DXF file path")
    p.add_argument("--entity1", help="First entity identifier (handle or block_name)")
    p.add_argument("--entity2", help="Second entity identifier (handle or block_name)")
    p.add_argument("--coord1", help="First coordinate 'x,y' or 'x,y,z'")
    p.add_argument("--coord2", help="Second coordinate 'x,y' or 'x,y,z'")
    
    # screenshot
    p = subparsers.add_parser("screenshot", help="Capture screenshot of specified entity/region")
    p.add_argument("file", help="DWG/DXF file path")
    p.add_argument("--block-name", help="Locate screenshot region by block name")
    p.add_argument("--handle", help="Locate screenshot region by entity handle")
    p.add_argument("--layer-name", help="Capture entire layer content region")
    p.add_argument("--region", help="Directly specify screenshot region 'x,y,w,h'")
    p.add_argument("--radius", type=float, default=5000, help="Expansion radius around entity")
    p.add_argument("--output", "-o", help="Output file path (default: cad_screenshot.png)")
    p.add_argument("--pixel-size", type=int, default=3000, help="Output image pixel size")
    p.add_argument("--background", default="black", help="Background color")
    p.add_argument("--qcad-path", help="QCAD dwg2bmp tool path")
    
    # audit
    p = subparsers.add_parser("audit", help="Drawing compliance audit")
    p.add_argument("file", help="DWG/DXF file path")
    
    # search
    p = subparsers.add_parser("search", help="Search entities by keyword")
    p.add_argument("file", help="DWG/DXF file path")
    p.add_argument("keyword", help="Search keyword")
    p.add_argument("--limit", type=int, help="Limit results")
    
    # export-pdf
    p = subparsers.add_parser("export-pdf", help="Export drawing to PDF")
    p.add_argument("file", help="DWG/DXF file path")
    p.add_argument("--output", "-o", help="Output PDF path (default: cad_export.pdf)")
    p.add_argument("--background", default="#FFFFFF", help="Background color")
    
    # check-env
    p = subparsers.add_parser("check-env", help="Check environment dependency status")
    
    # setup
    p = subparsers.add_parser("setup", help="Run environment setup (requires --confirm)")
    p.add_argument("--confirm", action="store_true", help="Explicitly confirm to run setup")
    p.add_argument("--skip-oda", action="store_true", help="Skip ODA File Converter installation")
    p.add_argument("--skip-qcad", action="store_true", help="Skip QCAD installation")
    p.add_argument("--oda-rpm", help="Specify local ODA RPM/DEB package path")
    p.add_argument("--qcad-tar", help="Specify local QCAD tar.gz package path")
    
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    cmd_map = {
        "info": cmd_info, "layers": cmd_layers, "entities": cmd_entities,
        "blocks": cmd_blocks, "inserts": cmd_inserts, "texts": cmd_texts,
        "layer-content": cmd_layer_content, "spaces": cmd_spaces, "distance": cmd_distance,
        "screenshot": cmd_screenshot, "audit": cmd_audit, "search": cmd_search,
        "export-pdf": cmd_export_pdf, "check-env": cmd_check_env, "setup": cmd_setup
    }
    cmd_map[args.command](args)


if __name__ == "__main__":
    main()
