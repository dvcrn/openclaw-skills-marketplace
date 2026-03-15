#!/bin/bash
# CashFlow - Personal cash flow tracker
DATA_DIR="$HOME/.cashflow"; mkdir -p "$DATA_DIR"
DATA_FILE="$DATA_DIR/transactions.json"
[ ! -f "$DATA_FILE" ] && echo "[]" > "$DATA_FILE"

cmd_income() {
    local amount=$1; shift; local note="$*"
    [ -z "$amount" ] && { echo "Usage: cashflow income <amount> [note]"; return 1; }
    python3 -c "
import json,time
e={'date':time.strftime('%Y-%m-%d'),'time':time.strftime('%H:%M'),'type':'income','amount':float('$amount'),'note':'$note'}
try:
 with open('$DATA_FILE') as f: d=json.load(f)
except: d=[]
d.append(e)
with open('$DATA_FILE','w') as f: json.dump(d,f,indent=2)
print('Income: +\${:.2f} {}'.format(float('$amount'),'$note'))
"
}
cmd_expense() {
    local amount=$1; shift; local note="$*"
    [ -z "$amount" ] && { echo "Usage: cashflow expense <amount> [note]"; return 1; }
    python3 -c "
import json,time
e={'date':time.strftime('%Y-%m-%d'),'time':time.strftime('%H:%M'),'type':'expense','amount':float('$amount'),'note':'$note'}
try:
 with open('$DATA_FILE') as f: d=json.load(f)
except: d=[]
d.append(e)
with open('$DATA_FILE','w') as f: json.dump(d,f,indent=2)
print('Expense: -\${:.2f} {}'.format(float('$amount'),'$note'))
"
}
cmd_balance() {
    python3 -c "
import json
try:
 with open('$DATA_FILE') as f: d=json.load(f)
except: d=[]
inc=sum(e['amount'] for e in d if e['type']=='income')
exp=sum(e['amount'] for e in d if e['type']=='expense')
print('Balance: \${:.2f}'.format(inc-exp))
print('  Income:  \${:.2f}'.format(inc))
print('  Expense: \${:.2f}'.format(exp))
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
if not t: print('No transactions today.')
else:
 for e in t: print('  {} \${:.2f} {}'.format('+' if e['type']=='income' else '-',e['amount'],e.get('note','')))
 inc=sum(e['amount'] for e in t if e['type']=='income')
 exp=sum(e['amount'] for e in t if e['type']=='expense')
 print('Today: +\${:.2f} / -\${:.2f} = \${:.2f}'.format(inc,exp,inc-exp))
"
}
cmd_month() {
    python3 -c "
import json,time
mo=time.strftime('%Y-%m')
try:
 with open('$DATA_FILE') as f: d=json.load(f)
except: d=[]
t=[e for e in d if e['date'][:7]==mo]
inc=sum(e['amount'] for e in t if e['type']=='income')
exp=sum(e['amount'] for e in t if e['type']=='expense')
print('This month ({})'.format(mo))
print('  Income:  \${:.2f}'.format(inc))
print('  Expense: \${:.2f}'.format(exp))
print('  Net:     \${:.2f}'.format(inc-exp))
"
}
cmd_history() {
    local n=${1:-10}
    python3 -c "
import json
try:
 with open('$DATA_FILE') as f: d=json.load(f)
except: d=[]
for e in d[-$n:]:
 print('{} {} \${:.2f} {}'.format(e['date'],'+' if e['type']=='income' else '-',e['amount'],e.get('note','')))
"
}
cmd_help() {
    echo "CashFlow - Personal Cash Flow Tracker"
    echo "Commands: income <amt> [note] | expense <amt> [note] | balance | today | month | history [n] | help"
}
cmd_info() { echo "CashFlow v1.0.0 | Powered by BytesAgain"; }
case "$1" in
    income) shift; cmd_income "$@";; expense) shift; cmd_expense "$@";;
    balance) cmd_balance;; today) cmd_today;; month) cmd_month;;
    history) shift; cmd_history "$@";; info) cmd_info;; help|"") cmd_help;;
    *) cmd_help; exit 1;;
esac
