#!/bin/bash
cmd_hex2rgb() { local hex="$1"; [ -z "$hex" ] && { echo "Usage: colorpick hex2rgb <#hex>"; return 1; }
    python3 -c "
h='$hex'.lstrip('#')
r,g,b=int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
print('#{} → rgb({},{},{})'.format(h,r,g,b))
print('\033[48;2;{};{};{}m     \033[0m'.format(r,g,b))
"; }
cmd_rgb2hex() { local r="$1" g="$2" b="$3"
    [ -z "$r" ] || [ -z "$g" ] || [ -z "$b" ] && { echo "Usage: colorpick rgb2hex <r> <g> <b>"; return 1; }
    python3 -c "print('rgb({},{},{}) → #{:02x}{:02x}{:02x}'.format(int('$r'),int('$g'),int('$b'),int('$r'),int('$g'),int('$b')))"; }
cmd_palette() { local base="$1"; [ -z "$base" ] && { echo "Usage: colorpick palette <#hex>"; return 1; }
    python3 -c "
h='$base'.lstrip('#')
r,g,b=int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
print('Color palette for #{}'.format(h))
for factor in [0.2,0.4,0.6,0.8,1.0]:
 nr,ng,nb=int(r*factor),int(g*factor),int(b*factor)
 print('  \033[48;2;{};{};{}m   \033[0m #{:02x}{:02x}{:02x} ({:.0f}%)'.format(nr,ng,nb,nr,ng,nb,factor*100))
for factor in [0.2,0.4,0.6,0.8]:
 nr=min(255,r+int((255-r)*factor))
 ng=min(255,g+int((255-g)*factor))
 nb=min(255,b+int((255-b)*factor))
 print('  \033[48;2;{};{};{}m   \033[0m #{:02x}{:02x}{:02x} (light {:.0f}%)'.format(nr,ng,nb,nr,ng,nb,factor*100))
"; }
cmd_random() { local n="${1:-5}"; python3 -c "
import random
for _ in range(int('$n')):
 r,g,b=random.randint(0,255),random.randint(0,255),random.randint(0,255)
 print('\033[48;2;{};{};{}m   \033[0m #{:02x}{:02x}{:02x} rgb({},{},{})'.format(r,g,b,r,g,b,r,g,b))
"; }
cmd_help() { echo "ColorPick - Color Converter & Palette"; echo "Commands: hex2rgb <hex> | rgb2hex <r> <g> <b> | palette <hex> | random [n] | help"; }
cmd_info() { echo "ColorPick v1.0.0 | Powered by BytesAgain"; }
case "$1" in hex2rgb) shift; cmd_hex2rgb "$@";; rgb2hex) shift; cmd_rgb2hex "$@";; palette) shift; cmd_palette "$@";; random) shift; cmd_random "$@";; info) cmd_info;; help|"") cmd_help;; *) cmd_help; exit 1;; esac
