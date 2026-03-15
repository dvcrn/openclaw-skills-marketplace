#!/bin/bash
# Context Bridge - Helper script for managing contexts
# Part of the Context Bridge OpenClaw skill

CONTEXT_DIR="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}/memory/contexts"
INDEX_FILE="$CONTEXT_DIR/index.json"

# Ensure context directory exists
mkdir -p "$CONTEXT_DIR"

# Initialize index if it doesn't exist
if [ ! -f "$INDEX_FILE" ]; then
    echo '{"contexts": [], "updated": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' > "$INDEX_FILE"
fi

# Function: List all contexts
list_contexts() {
    if [ ! -f "$INDEX_FILE" ]; then
        echo "No contexts found."
        return
    fi
    
    echo "📚 Saved Contexts:"
    echo ""
    jq -r '.contexts[] | "• \(.project) (Updated: \(.updated | split("T")[0]))\n  \(.description)"' "$INDEX_FILE"
}

# Function: Save current context
save_context() {
    local project_name="$1"
    local description="${2:-No description}"
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    local context_file="$CONTEXT_DIR/${project_name}.json"
    
    # Create context data
    cat > "$context_file" <<EOF
{
  "project": "$project_name",
  "created": "$timestamp",
  "updated": "$timestamp",
  "description": "$description",
  "sessions": [],
  "decisions": [],
  "related_contexts": [],
  "tags": [],
  "files_changed": []
}
EOF
    
    # Update index
    local temp_index=$(mktemp)
    jq --arg proj "$project_name" --arg desc "$description" --arg time "$timestamp" \
        '.contexts += [{"project": $proj, "description": $desc, "updated": $time}] | 
         .contexts |= unique_by(.project) | 
         .updated = $time' \
        "$INDEX_FILE" > "$temp_index"
    mv "$temp_index" "$INDEX_FILE"
    
    echo "✅ Context saved: $project_name"
    echo "📁 Location: $context_file"
}

# Function: Load context
load_context() {
    local project_name="$1"
    local context_file="$CONTEXT_DIR/${project_name}.json"
    
    if [ ! -f "$context_file" ]; then
        echo "❌ Context not found: $project_name"
        echo "💡 Use: context-bridge list to see available contexts"
        return 1
    fi
    
    echo "🌉 Loading context: $project_name"
    echo ""
    
    # Display context summary
    jq -r '"Project: \(.project)
Created: \(.created | split("T")[0])
Last Updated: \(.updated | split("T")[0])
Description: \(.description)
Sessions: \(.sessions | length)
Decisions: \(.decisions | length)
Files Changed: \(.files_changed | length)
"' "$context_file"
    
    # Display recent decisions
    local decision_count=$(jq '.decisions | length' "$context_file")
    if [ "$decision_count" -gt 0 ]; then
        echo "📝 Recent Decisions:"
        jq -r '.decisions[-3:] | .[] | "  • \(.decision) (\(.date | split("T")[0]))"' "$context_file"
        echo ""
    fi
    
    # Display tags
    local tag_count=$(jq '.tags | length' "$context_file")
    if [ "$tag_count" -gt 0 ]; then
        echo "🏷️  Tags: $(jq -r '.tags | join(", ")' "$context_file")"
        echo ""
    fi
    
    echo "📄 Full context available at: $context_file"
}

# Function: Search contexts
search_contexts() {
    local query="$1"
    echo "🔍 Searching contexts for: $query"
    echo ""
    
    find "$CONTEXT_DIR" -name "*.json" -not -name "index.json" | while read -r file; do
        if jq -e --arg q "$query" '
            (.project | contains($q)) or 
            (.description | contains($q)) or 
            (.tags | any(. | contains($q))) or
            (.decisions | any(.decision | contains($q)))
        ' "$file" > /dev/null 2>&1; then
            local project=$(jq -r '.project' "$file")
            local desc=$(jq -r '.description' "$file")
            echo "✓ $project"
            echo "  $desc"
            echo ""
        fi
    done
}

# Function: Show decisions for a context
show_decisions() {
    local project_name="$1"
    local context_file="$CONTEXT_DIR/${project_name}.json"
    
    if [ ! -f "$context_file" ]; then
        echo "❌ Context not found: $project_name"
        return 1
    fi
    
    echo "📋 Decision Timeline for: $project_name"
    echo ""
    
    jq -r '.decisions[] | "[\(.date | split("T")[0])] \(.decision)\n  Reasoning: \(.reasoning)\n"' "$context_file"
}

# Function: Add decision to context
add_decision() {
    local project_name="$1"
    local decision="$2"
    local reasoning="${3:-No reasoning provided}"
    local context_file="$CONTEXT_DIR/${project_name}.json"
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    
    if [ ! -f "$context_file" ]; then
        echo "❌ Context not found: $project_name"
        return 1
    fi
    
    local temp_file=$(mktemp)
    jq --arg dec "$decision" --arg reas "$reasoning" --arg time "$timestamp" \
        '.decisions += [{
            "decision": $dec,
            "reasoning": $reas,
            "date": $time,
            "alternatives": []
        }] | .updated = $time' \
        "$context_file" > "$temp_file"
    mv "$temp_file" "$context_file"
    
    echo "✅ Decision added to $project_name"
}

# Function: Add tags
add_tags() {
    local project_name="$1"
    shift
    local tags=("$@")
    local context_file="$CONTEXT_DIR/${project_name}.json"
    
    if [ ! -f "$context_file" ]; then
        echo "❌ Context not found: $project_name"
        return 1
    fi
    
    local temp_file=$(mktemp)
    local tag_json=$(printf '%s\n' "${tags[@]}" | jq -R . | jq -s .)
    jq --argjson new_tags "$tag_json" \
        '.tags = (.tags + $new_tags | unique)' \
        "$context_file" > "$temp_file"
    mv "$temp_file" "$context_file"
    
    echo "✅ Tags added: ${tags[*]}"
}

# Function: Export context to markdown
export_context() {
    local project_name="$1"
    local output_file="${2:-${project_name}-export.md}"
    local context_file="$CONTEXT_DIR/${project_name}.json"
    
    if [ ! -f "$context_file" ]; then
        echo "❌ Context not found: $project_name"
        return 1
    fi
    
    cat > "$output_file" <<EOF
# Context: $(jq -r '.project' "$context_file")

**Description:** $(jq -r '.description' "$context_file")  
**Created:** $(jq -r '.created | split("T")[0]' "$context_file")  
**Last Updated:** $(jq -r '.updated | split("T")[0]' "$context_file")

## Overview

- **Sessions:** $(jq '.sessions | length' "$context_file")
- **Decisions:** $(jq '.decisions | length' "$context_file")
- **Files Changed:** $(jq '.files_changed | length' "$context_file")

## Decisions

$(jq -r '.decisions[] | "### \(.decision)\n\n**Date:** \(.date | split("T")[0])  \n**Reasoning:** \(.reasoning)\n"' "$context_file")

## Tags

$(jq -r '.tags | map("- " + .) | join("\n")' "$context_file")

## Related Contexts

$(jq -r '.related_contexts | map("- " + .) | join("\n")' "$context_file")

---

*Exported from Context Bridge on $(date)*
EOF
    
    echo "✅ Context exported to: $output_file"
}

# Main command dispatcher
case "$1" in
    save)
        save_context "$2" "$3"
        ;;
    load|resume)
        load_context "$2"
        ;;
    list)
        list_contexts
        ;;
    search)
        search_contexts "$2"
        ;;
    decisions)
        show_decisions "$2"
        ;;
    add-decision)
        add_decision "$2" "$3" "$4"
        ;;
    tag)
        shift
        project="$1"
        shift
        add_tags "$project" "$@"
        ;;
    export)
        export_context "$2" "$3"
        ;;
    *)
        echo "Context Bridge - Context Management Tool"
        echo ""
        echo "Usage:"
        echo "  context-bridge save <project-name> [description]"
        echo "  context-bridge load <project-name>"
        echo "  context-bridge list"
        echo "  context-bridge search <query>"
        echo "  context-bridge decisions <project-name>"
        echo "  context-bridge add-decision <project> <decision> [reasoning]"
        echo "  context-bridge tag <project> <tag1> [tag2...]"
        echo "  context-bridge export <project-name> [output-file]"
        echo ""
        echo "Examples:"
        echo "  context-bridge save api-redesign 'Switching to GraphQL'"
        echo "  context-bridge load api-redesign"
        echo "  context-bridge search authentication"
        echo "  context-bridge decisions api-redesign"
        echo "  context-bridge tag api-redesign backend graphql"
        echo "  context-bridge export api-redesign report.md"
        ;;
esac
