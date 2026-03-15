#!/bin/bash
# BudgetLy - Smart budget manager
DATA_DIR="$HOME/.budgetly"; mkdir -p "$DATA_DIR"
DATA_FILE="$DATA_DIR/budgets.json"
TXN_FILE="$DATA_DIR/transactions.json"
[ ! -f "$DATA_FILE" ] && echo "{}" > "$DATA_FILE"
[ ! -f "$TXN_FILE" ] && echo "[]" > "$TXN_FILE"

cmd_set() {
    local cat="$1"; local amount="$2"
    [ -z "$cat" ] || [ -z "$amount" ] && { echo "Usage: budgetly set <category> <amount>"; return 1; }
    python3 -c "
import json
try:
 with open('$DATA_FILE') as f: d=json.load(f)
except: d={}
d['$cat']=float('$amount')
with open('$DATA_FILE','w') as f: json.dump(d,f,indent=2)
print('Budget set: $cat = \${}'.format('$amount'))
"
}
cmd_spend() {
    local cat="$1"; local amount="$2"; shift 2; local note="$*"
    [ -z "$cat" ] || [ -z "$amount" ] && { echo "Usage: budgetly spend <category> <amount> [note]"; return 1; }
    python3 -c "
import json,time
e={'date':time.strftime('%Y-%m-%d'),'category':'$cat','amount':float('$amount'),'note':'$note'}
try:
 with open('$TXN_FILE') as f: d=json.load(f)
except: d=[]
d.append(e)
with open('$TXN_FILE','w') as f: json.dump(d,f,indent=2)
print('Spent \${} on $cat {}'.format('$amount','$note'))
"
}
cmd_status() {
    python3 -c "
import json,time
mo=time.strftime('%Y-%m')
try:
 with open('$DATA_FILE') as f: budgets=json.load(f)
except: budgets={}
try:
 with open('$TXN_FILE') as f: txns=json.load(f)
except: txns=[]
month_txns=[t for t in txns if t['date'][:7]==mo]
spent={}
for t in month_txns: spent[t['category']]=spent.get(t['category'],0)+t['amount']
print('Budget Status ({})'.format(mo))
print('-'*40)
for cat,budget in sorted(budgets.items()):
 s=spent.get(cat,0)
 pct=s/budget*100 if budget>0 else 0
 bar='█'*int(pct/10)+'░'*(10-int(pct/10))
 warn=' ⚠️' if pct>80 else ' 🔴' if pct>100 else ''
 print('  {:12s} \${:>8.2f}/\${:>8.2f} [{}] {:>5.1f}%{}'.format(cat,s,budget,bar,pct,warn))
uncat={k:v for k,v in spent.items() if k not in budgets}
if uncat:
 print('\n  Unbudgeted:')
 for k,v in uncat.items(): print('    {:12s} \${:.2f}'.format(k,v))
"
}
cmd_report() {
    python3 -c "
import json,time
mo=time.strftime('%Y-%m')
try:
 with open('$TXN_FILE') as f: txns=json.load(f)
except: txns=[]
month_txns=[t for t in txns if t['date'][:7]==mo]
total=sum(t['amount'] for t in month_txns)
by_cat={}
for t in month_txns: by_cat[t['category']]=by_cat.get(t['category'],0)+t['amount']
print('Monthly Report ({})'.format(mo))
print('  Total spent: \${:.2f}'.format(total))
print('  Categories:')
for k,v in sorted(by_cat.items(),key=lambda x:-x[1]):
 pct=v/total*100 if total>0 else 0
 print('    {:12s} \${:>8.2f} ({:.1f}%)'.format(k,v,pct))
"
}
cmd_help() {
    echo "BudgetLy - Smart Budget Manager"
    echo "Commands: set <category> <amount> | spend <category> <amount> [note] | status | report | help"
}
cmd_info() { echo "BudgetLy v1.0.0 | Powered by BytesAgain"; }
case "$1" in
    set) shift; cmd_set "$@";; spend) shift; cmd_spend "$@";;
    status) cmd_status;; report) cmd_report;; info) cmd_info;; help|"") cmd_help;;
    *) cmd_help; exit 1;;
esac
