#!/bin/bash
# MindMap - Text-based mind mapping tool
DATA_DIR="$HOME/.mindmap"; mkdir -p "$DATA_DIR"
MAPS_FILE="$DATA_DIR/maps.json"
[ ! -f "$MAPS_FILE" ] && echo "{}" > "$MAPS_FILE"

cmd_create() {
    local name="$*"
    [ -z "$name" ] && { echo "Usage: mindmap create <name>"; return 1; }
    python3 -c "
import json
try:
 with open('$MAPS_FILE') as f: d=json.load(f)
except: d={}
d['$name']={'children':{}}
with open('$MAPS_FILE','w') as f: json.dump(d,f,indent=2)
print('Mind map created: $name')
"
}
cmd_add() {
    local map="$1"; shift; local parent="$1"; shift; local node="$*"
    [ -z "$node" ] && { echo "Usage: mindmap add <map> <parent> <node>"; return 1; }
    python3 -c "
import json
def find_add(tree,parent,node):
 if parent=='root': tree[node]={'children':{}}; return True
 for k,v in tree.items():
  if k==parent: v.setdefault('children',{})[node]={'children':{}}; return True
  if find_add(v.get('children',{}),parent,node): return True
 return False
try:
 with open('$MAPS_FILE') as f: d=json.load(f)
except: d={}
if '$map' not in d: print('Map not found: $map')
else:
 if find_add(d['$map']['children'],'$parent','$node'): print('Added: $node -> $parent')
 else: print('Parent not found: $parent')
 with open('$MAPS_FILE','w') as f: json.dump(d,f,indent=2)
"
}
cmd_show() {
    local name="$*"
    [ -z "$name" ] && { echo "Usage: mindmap show <name>"; return 1; }
    python3 -c "
import json
def render(tree,prefix='',last=True):
 items=list(tree.items())
 for i,(k,v) in enumerate(items):
  is_last=(i==len(items)-1)
  connector='└── ' if is_last else '├── '
  print(prefix+connector+k)
  ext='    ' if is_last else '│   '
  render(v.get('children',{}),prefix+ext,is_last)
try:
 with open('$MAPS_FILE') as f: d=json.load(f)
except: d={}
if '$name' not in d: print('Map not found: $name')
else:
 print('🧠 $name')
 render(d['$name']['children'])
"
}
cmd_list() {
    python3 -c "
import json
try:
 with open('$MAPS_FILE') as f: d=json.load(f)
except: d={}
if not d: print('No mind maps yet.')
else:
 for k in d: print('  🧠 {}'.format(k))
"
}
cmd_export() {
    local name="$*"
    [ -z "$name" ] && { echo "Usage: mindmap export <name>"; return 1; }
    python3 -c "
import json
def to_md(tree,level=0):
 for k,v in tree.items():
  print('  '*level+'- '+k)
  to_md(v.get('children',{}),level+1)
try:
 with open('$MAPS_FILE') as f: d=json.load(f)
except: d={}
if '$name' not in d: print('Map not found')
else:
 print('# $name')
 to_md(d['$name']['children'])
"
}
cmd_help() {
    echo "MindMap - Text-Based Mind Mapping"
    echo "Commands: create <name> | add <map> <parent> <node> | show <name> | list | export <name> | help"
    echo "Use 'root' as parent to add top-level nodes"
}
cmd_info() { echo "MindMap v1.0.0 | Powered by BytesAgain"; }
case "$1" in
    create) shift; cmd_create "$@";; add) shift; cmd_add "$@";;
    show) shift; cmd_show "$@";; list) cmd_list;; export) shift; cmd_export "$@";;
    info) cmd_info;; help|"") cmd_help;; *) cmd_help; exit 1;;
esac
