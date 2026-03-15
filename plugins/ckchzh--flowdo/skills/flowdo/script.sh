#!/bin/bash
# FlowDo - Task and workflow manager
DATA_DIR="$HOME/.flowdo"; mkdir -p "$DATA_DIR"
TASKS_FILE="$DATA_DIR/tasks.json"
[ ! -f "$TASKS_FILE" ] && echo "[]" > "$TASKS_FILE"

cmd_add() {
    local text="$*"
    [ -z "$text" ] && { echo "Usage: flowdo add <task description>"; return 1; }
    python3 -c "
import json,time
t={'id':int(time.time()),'text':'$text','status':'todo','priority':'normal','created':time.strftime('%Y-%m-%d'),'tags':[]}
try:
 with open('$TASKS_FILE') as f: d=json.load(f)
except: d=[]
d.append(t)
with open('$TASKS_FILE','w') as f: json.dump(d,f,indent=2)
print('Task added: $text')
"
}
cmd_done() {
    local id=$1
    [ -z "$id" ] && { echo "Usage: flowdo done <task_id>"; return 1; }
    python3 -c "
import json
try:
 with open('$TASKS_FILE') as f: d=json.load(f)
except: d=[]
for t in d:
 if str(t['id'])=='$id': t['status']='done'; print('Done: '+t['text']); break
with open('$TASKS_FILE','w') as f: json.dump(d,f,indent=2)
"
}
cmd_list() {
    local filter="${1:-all}"
    python3 -c "
import json
try:
 with open('$TASKS_FILE') as f: d=json.load(f)
except: d=[]
filt='$filter'
if filt!='all': d=[t for t in d if t['status']==filt]
if not d: print('No tasks.')
else:
 icons={'todo':'⬜','doing':'🔄','done':'✅','blocked':'🚫'}
 for t in d:
  icon=icons.get(t['status'],'?')
  pri='❗' if t.get('priority')=='high' else ''
  print('{} [{}] {}{}'.format(icon,t['id'],pri,t['text']))
"
}
cmd_doing() {
    local id=$1
    [ -z "$id" ] && { echo "Usage: flowdo doing <task_id>"; return 1; }
    python3 -c "
import json
try:
 with open('$TASKS_FILE') as f: d=json.load(f)
except: d=[]
for t in d:
 if str(t['id'])=='$id': t['status']='doing'; print('In progress: '+t['text']); break
with open('$TASKS_FILE','w') as f: json.dump(d,f,indent=2)
"
}
cmd_priority() {
    local id=$1; local pri=${2:-high}
    [ -z "$id" ] && { echo "Usage: flowdo priority <id> <high|normal|low>"; return 1; }
    python3 -c "
import json
try:
 with open('$TASKS_FILE') as f: d=json.load(f)
except: d=[]
for t in d:
 if str(t['id'])=='$id': t['priority']='$pri'; print('Priority set to $pri'); break
with open('$TASKS_FILE','w') as f: json.dump(d,f,indent=2)
"
}
cmd_stats() {
    python3 -c "
import json
from collections import Counter
try:
 with open('$TASKS_FILE') as f: d=json.load(f)
except: d=[]
c=Counter(t['status'] for t in d)
print('FlowDo Stats:')
print('  Total: {} | Todo: {} | Doing: {} | Done: {} | Blocked: {}'.format(len(d),c.get('todo',0),c.get('doing',0),c.get('done',0),c.get('blocked',0)))
if d:
 done_pct=c.get('done',0)/len(d)*100
 print('  Completion: {:.0f}%'.format(done_pct))
"
}
cmd_help() {
    echo "FlowDo - Task & Workflow Manager"
    echo "Commands: add <text> | list [todo|doing|done] | done <id> | doing <id> | priority <id> <level> | stats | help"
}
cmd_info() { echo "FlowDo v1.0.0 | Powered by BytesAgain"; }
case "$1" in
    add) shift; cmd_add "$@";; done) shift; cmd_done "$@";; doing) shift; cmd_doing "$@";;
    list) shift; cmd_list "$@";; priority) shift; cmd_priority "$@";;
    stats) cmd_stats;; info) cmd_info;; help|"") cmd_help;; *) cmd_help; exit 1;;
esac
