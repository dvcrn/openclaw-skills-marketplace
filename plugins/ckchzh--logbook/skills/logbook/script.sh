#!/bin/bash
# LogBook - Personal digital logbook
DATA_DIR="$HOME/.logbook"; mkdir -p "$DATA_DIR"
LOG_FILE="$DATA_DIR/entries.json"
[ ! -f "$LOG_FILE" ] && echo "[]" > "$LOG_FILE"

cmd_write() {
    local text="$*"
    [ -z "$text" ] && { echo "Usage: logbook write <your entry>"; return 1; }
    python3 -c "
import json,time
e={'date':time.strftime('%Y-%m-%d'),'time':time.strftime('%H:%M'),'text':'$text','tags':[]}
try:
 with open('$LOG_FILE') as f: d=json.load(f)
except: d=[]
d.append(e)
with open('$LOG_FILE','w') as f: json.dump(d,f,indent=2)
print('Logged at {}'.format(time.strftime('%Y-%m-%d %H:%M')))
"
}
cmd_today() {
    python3 -c "
import json,time
today=time.strftime('%Y-%m-%d')
try:
 with open('$LOG_FILE') as f: d=json.load(f)
except: d=[]
t=[e for e in d if e['date']==today]
if not t: print('No entries today.')
else:
 for e in t: print('[{}] {}'.format(e['time'],e['text']))
 print('---\n{} entries today'.format(len(t)))
"
}
cmd_search() {
    local q="$*"
    [ -z "$q" ] && { echo "Usage: logbook search <keyword>"; return 1; }
    python3 -c "
import json
try:
 with open('$LOG_FILE') as f: d=json.load(f)
except: d=[]
r=[e for e in d if '$q'.lower() in e['text'].lower()]
if not r: print('No matches for: $q')
else:
 for e in r: print('{} [{}] {}'.format(e['date'],e['time'],e['text']))
 print('---\n{} matches'.format(len(r)))
"
}
cmd_week() {
    python3 -c "
import json,datetime
try:
 with open('$LOG_FILE') as f: d=json.load(f)
except: d=[]
cutoff=(datetime.date.today()-datetime.timedelta(days=7)).strftime('%Y-%m-%d')
r=[e for e in d if e['date']>=cutoff]
if not r: print('No entries this week.')
else:
 cur=''
 for e in sorted(r,key=lambda x:x['date']+x['time']):
  if e['date']!=cur: cur=e['date']; print('\n'+cur)
  print('  [{}] {}'.format(e['time'],e['text']))
 print('---\n{} entries this week'.format(len(r)))
"
}
cmd_stats() {
    python3 -c "
import json
from collections import Counter
try:
 with open('$LOG_FILE') as f: d=json.load(f)
except: d=[]
dates=Counter(e['date'] for e in d)
print('LogBook Stats:')
print('  Total entries: {}'.format(len(d)))
print('  Days logged: {}'.format(len(dates)))
if dates:
 print('  Most active: {} ({} entries)'.format(*dates.most_common(1)[0]))
 print('  Avg/day: {:.1f}'.format(len(d)/len(dates)))
"
}
cmd_export() {
    python3 -c "
import json
try:
 with open('$LOG_FILE') as f: d=json.load(f)
except: d=[]
print('# LogBook Export\n')
cur=''
for e in sorted(d,key=lambda x:x['date']+x['time']):
 if e['date']!=cur: cur=e['date']; print('## '+cur)
 print('- [{}] {}'.format(e['time'],e['text']))
"
}
cmd_help() {
    echo "LogBook - Personal Digital Logbook"
    echo "Commands: write <text> | today | week | search <keyword> | stats | export | help"
}
cmd_info() { echo "LogBook v1.0.0 | Powered by BytesAgain"; }
case "$1" in
    write) shift; cmd_write "$@";; today) cmd_today;; week) cmd_week;;
    search) shift; cmd_search "$@";; stats) cmd_stats;; export) cmd_export;;
    info) cmd_info;; help|"") cmd_help;; *) cmd_help; exit 1;;
esac
