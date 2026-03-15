#!/bin/bash
# SleepWell - Sleep tracker
DATA_DIR="$HOME/.sleepwell"; mkdir -p "$DATA_DIR"
DATA_FILE="$DATA_DIR/sleep.json"
[ ! -f "$DATA_FILE" ] && echo "[]" > "$DATA_FILE"

cmd_log() {
    local bedtime="$1"; local wakeup="$2"; local quality="${3:-3}"
    [ -z "$bedtime" ] || [ -z "$wakeup" ] && { echo "Usage: sleepwell log <bedtime> <wakeup> [quality 1-5]"; echo "Example: sleepwell log 23:00 07:00 4"; return 1; }
    python3 -c "
import json,time,datetime
bt='$bedtime'; wu='$wakeup'
try:
 b=datetime.datetime.strptime(bt,'%H:%M')
 w=datetime.datetime.strptime(wu,'%H:%M')
 diff=(w-b).seconds/3600
 if diff<0: diff+=24
except: diff=0
e={'date':time.strftime('%Y-%m-%d'),'bedtime':bt,'wakeup':wu,'hours':round(diff,1),'quality':int('$quality')}
try:
 with open('$DATA_FILE') as f: d=json.load(f)
except: d=[]
d.append(e)
with open('$DATA_FILE','w') as f: json.dump(d,f,indent=2)
print('Logged: {}h sleep (quality {}/5)'.format(round(diff,1),'$quality'))
"
}
cmd_today() {
    python3 -c "
import json,time
today=time.strftime('%Y-%m-%d')
try:
 with open('$DATA_FILE') as f: d=json.load(f)
except: d=[]
t=[e for e in d if e['date']==today]
if not t: print('No sleep logged today.')
else:
 for e in t:
  stars='⭐'*e['quality']
  print('  {}→{} ({}h) {}'.format(e['bedtime'],e['wakeup'],e['hours'],stars))
"
}
cmd_week() {
    python3 -c "
import json,datetime
try:
 with open('$DATA_FILE') as f: d=json.load(f)
except: d=[]
cutoff=(datetime.date.today()-datetime.timedelta(days=7)).strftime('%Y-%m-%d')
r=[e for e in d if e['date']>=cutoff]
if not r: print('No sleep data this week.')
else:
 total_h=sum(e['hours'] for e in r)
 avg_h=total_h/len(r)
 avg_q=sum(e['quality'] for e in r)/len(r)
 print('Weekly Sleep Summary:')
 for e in sorted(r,key=lambda x:x['date']):
  bar='█'*int(e['hours'])
  print('  {} {} {}h (q:{})'.format(e['date'][-5:],bar,e['hours'],e['quality']))
 print('  Avg: {:.1f}h/night, quality {:.1f}/5'.format(avg_h,avg_q))
 if avg_h<7: print('  ⚠️ Below recommended 7-9 hours!')
"
}
cmd_stats() {
    python3 -c "
import json
try:
 with open('$DATA_FILE') as f: d=json.load(f)
except: d=[]
if not d: print('No data yet.')
else:
 hours=[e['hours'] for e in d]
 quals=[e['quality'] for e in d]
 print('Sleep Stats ({} nights):'.format(len(d)))
 print('  Avg duration: {:.1f}h'.format(sum(hours)/len(hours)))
 print('  Avg quality: {:.1f}/5'.format(sum(quals)/len(quals)))
 print('  Best night: {}h'.format(max(hours)))
 print('  Worst night: {}h'.format(min(hours)))
 good=sum(1 for h in hours if 7<=h<=9)
 print('  In range (7-9h): {:.0f}%'.format(good/len(hours)*100))
"
}
cmd_tips() {
    tips=("Maintain a consistent sleep schedule" "Avoid screens 1 hour before bed" "Keep bedroom cool (65-68°F)" "Limit caffeine after 2pm" "Exercise regularly but not before bed" "Try relaxation techniques" "Avoid large meals before sleep")
    echo "💤 Sleep Tip: ${tips[$((RANDOM % ${#tips[@]}))]}"
}
cmd_help() {
    echo "SleepWell - Sleep Tracker"
    echo "Commands: log <bedtime> <wakeup> [quality] | today | week | stats | tips | help"
    echo "Example: sleepwell log 23:00 07:00 4"
}
cmd_info() { echo "SleepWell v1.0.0 | Powered by BytesAgain"; }
case "$1" in
    log) shift; cmd_log "$@";; today) cmd_today;; week) cmd_week;;
    stats) cmd_stats;; tips) cmd_tips;; info) cmd_info;; help|"") cmd_help;;
    *) cmd_help; exit 1;;
esac
