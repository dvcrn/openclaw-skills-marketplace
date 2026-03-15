#!/bin/bash
cmd_check() { local domain="$1"; [ -z "$domain" ] && { echo "Usage: certcheck check <domain>"; return 1; }
    python3 -c "
import ssl,socket,datetime
ctx=ssl.create_default_context()
try:
 with ctx.wrap_socket(socket.socket(),server_hostname='$domain') as s:
  s.settimeout(10)
  s.connect(('$domain',443))
  cert=s.getpeercert()
  print('SSL Certificate: $domain')
  print('  Subject: {}'.format(dict(x[0] for x in cert['subject']).get('commonName','')))
  print('  Issuer: {}'.format(dict(x[0] for x in cert['issuer']).get('organizationName','')))
  print('  Valid from: {}'.format(cert['notBefore']))
  print('  Valid until: {}'.format(cert['notAfter']))
  expires=datetime.datetime.strptime(cert['notAfter'],'%b %d %H:%M:%S %Y %Z')
  days=(expires-datetime.datetime.now()).days
  print('  Days remaining: {}'.format(days))
  if days<7: print('  🔴 CRITICAL: Expires in {} days!'.format(days))
  elif days<30: print('  ⚠️ WARNING: Expires in {} days'.format(days))
  else: print('  ✅ Valid')
  if cert.get('subjectAltName'):
   sans=[x[1] for x in cert['subjectAltName']]
   print('  SANs: {}'.format(', '.join(sans[:5])))
   if len(sans)>5: print('    ...and {} more'.format(len(sans)-5))
  print('  Protocol: {}'.format(s.version()))
except Exception as e: print('❌ SSL check failed: {}'.format(e))
"; }
cmd_expiry() { local domain="$1"; [ -z "$domain" ] && { echo "Usage: certcheck expiry <domain>"; return 1; }
    python3 -c "
import ssl,socket,datetime
ctx=ssl.create_default_context()
try:
 with ctx.wrap_socket(socket.socket(),server_hostname='$domain') as s:
  s.settimeout(10); s.connect(('$domain',443))
  cert=s.getpeercert()
  expires=datetime.datetime.strptime(cert['notAfter'],'%b %d %H:%M:%S %Y %Z')
  days=(expires-datetime.datetime.now()).days
  icon='✅' if days>30 else '⚠️' if days>7 else '🔴'
  print('{} {} — {} days remaining (expires {})'.format(icon,'$domain',days,expires.strftime('%Y-%m-%d')))
except Exception as e: print('❌ $domain — {}'.format(e))
"; }
cmd_chain() { local domain="$1"; [ -z "$domain" ] && { echo "Usage: certcheck chain <domain>"; return 1; }
    echo "=== Certificate Chain: $domain ==="
    echo | openssl s_client -connect "$domain:443" -servername "$domain" -showcerts 2>/dev/null | grep -E 's:|i:' | head -10 || echo "openssl not available"
}
cmd_batch() { local file="$1"; [ -z "$file" ] || [ ! -f "$file" ] && { echo "Usage: certcheck batch <domains_file>"; return 1; }
    while IFS= read -r domain; do [ -n "$domain" ] && cmd_expiry "$domain"; done < "$file"
}
cmd_help() { echo "CertCheck - SSL Certificate Checker"; echo "Commands: check <domain> | expiry <domain> | chain <domain> | batch <file> | help"; }
cmd_info() { echo "CertCheck v1.0.0 | Powered by BytesAgain"; }
case "$1" in check) shift; cmd_check "$@";; expiry) shift; cmd_expiry "$@";; chain) shift; cmd_chain "$@";; batch) shift; cmd_batch "$@";; info) cmd_info;; help|"") cmd_help;; *) cmd_help; exit 1;; esac
