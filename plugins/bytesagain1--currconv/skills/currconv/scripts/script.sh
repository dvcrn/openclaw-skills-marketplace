#!/bin/bash
cmd_convert() { local amount="$1" from="$2" to="$3"
    [ -z "$amount" ] || [ -z "$from" ] || [ -z "$to" ] && { echo "Usage: currconv convert <amount> <from> <to>"; return 1; }
    python3 -c "
import urllib.request,json
from_c='$from'.upper(); to_c='$to'.upper()
try:
 url='https://open.er-api.com/v6/latest/{}'.format(from_c)
 data=json.loads(urllib.request.urlopen(url,timeout=10).read())
 if data.get('result')=='success':
  rate=data['rates'].get(to_c)
  if rate:
   result=float('$amount')*rate
   print('{} {} = {:.2f} {}'.format('$amount',from_c,result,to_c))
   print('Rate: 1 {} = {:.6f} {}'.format(from_c,rate,to_c))
  else: print('Currency not found: {}'.format(to_c))
 else: print('API error')
except Exception as e: print('Error: {}'.format(e))
"; }
cmd_rate() { local from="$1" to="$2"
    [ -z "$from" ] || [ -z "$to" ] && { echo "Usage: currconv rate <from> <to>"; return 1; }
    cmd_convert 1 "$from" "$to"
}
cmd_rates() { local base="${1:-USD}"
    python3 -c "
import urllib.request,json
base='$base'.upper()
try:
 url='https://open.er-api.com/v6/latest/{}'.format(base)
 data=json.loads(urllib.request.urlopen(url,timeout=10).read())
 rates=data.get('rates',{})
 majors=['USD','EUR','GBP','JPY','CNY','KRW','AUD','CAD','CHF','HKD','SGD','INR','BRL','MXN']
 print('Exchange rates (base: {}):'.format(base))
 for c in majors:
  if c!=base and c in rates:
   print('  {} = {:.4f}'.format(c,rates[c]))
except Exception as e: print('Error: {}'.format(e))
"; }
cmd_help() { echo "CurrConv - Currency Converter"; echo "Commands: convert <amount> <from> <to> | rate <from> <to> | rates [base] | help"; echo "Example: currconv convert 100 USD EUR"; }
cmd_info() { echo "CurrConv v1.0.0 | Powered by BytesAgain"; }
case "$1" in convert) shift; cmd_convert "$@";; rate) shift; cmd_rate "$@";; rates) shift; cmd_rates "$@";; info) cmd_info;; help|"") cmd_help;; *) cmd_help; exit 1;; esac
