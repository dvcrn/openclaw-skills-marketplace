#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./setup_local_pull.sh <vps-host-or-ip> <ssh-key-path> <destination-path> [interval-minutes]
# Example:
#   ./setup_local_pull.sh 134.199.174.28 ~/.ssh/do-reolink-relay /mnt/personalcloud-reolink/reolink 10

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <vps-host-or-ip> <ssh-key-path> <destination-path> [interval-minutes]"
  exit 1
fi

VPS_HOST="$1"
SSH_KEY="$2"
DEST_PATH="$3"
INTERVAL_MIN="${4:-10}"

mkdir -p "$HOME/bin" "$HOME/.config/systemd/user" "$DEST_PATH"

cat >"$HOME/bin/reolink_pull.sh" <<EOF
#!/usr/bin/env bash
set -euo pipefail

VPS_HOST="${VPS_HOST}"
VPS_USER="root"
VPS_SRC="/srv/reolink/incoming/"
SSH_KEY="${SSH_KEY}"
DST="${DEST_PATH}/"
LOG="${HOME}/reolink-sync.log"
LOCK="/tmp/reolink_pull.lock"

exec 9>"\$LOCK"
flock -n 9 || exit 0

log(){ echo "\$(date -Is) \$*" >> "\$LOG"; }

if ! mountpoint -q "$(dirname "${DEST_PATH}")" && ! mountpoint -q "${DEST_PATH}"; then
  log "ERROR destination mount missing: ${DEST_PATH}"
  exit 1
fi

mkdir -p "\$DST"

for i in 1 2 3; do
  if rsync -az --remove-source-files --partial --append-verify \
      -e "ssh -i \${SSH_KEY} -o BatchMode=yes -o ConnectTimeout=20" \
      "\${VPS_USER}@\${VPS_HOST}:\${VPS_SRC}" "\$DST" >> "\$LOG" 2>&1; then
    log "OK rsync pass \$i"
    break
  fi
  log "WARN rsync failed pass \$i"
  sleep \$((i*20))
done

ssh -i "\${SSH_KEY}" -o BatchMode=yes -o ConnectTimeout=20 "\${VPS_USER}@\${VPS_HOST}" \
  'find /srv/reolink/incoming -type d -empty -delete' >> "\$LOG" 2>&1 || log "WARN cleanup skipped"

log "DONE"
EOF

chmod +x "$HOME/bin/reolink_pull.sh"

cat >"$HOME/.config/systemd/user/reolink-pull.service" <<'EOF'
[Unit]
Description=Pull Reolink files from VPS to destination storage

[Service]
Type=oneshot
ExecStart=%h/bin/reolink_pull.sh
EOF

cat >"$HOME/.config/systemd/user/reolink-pull.timer" <<EOF
[Unit]
Description=Run Reolink pull every ${INTERVAL_MIN} minutes (persistent)

[Timer]
OnCalendar=*:0/${INTERVAL_MIN}
Persistent=true
RandomizedDelaySec=30

[Install]
WantedBy=timers.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now reolink-pull.timer

echo
systemctl --user list-timers | grep reolink-pull || true

echo
cat <<EOM
Done.
Next:
  1) Test once manually: $HOME/bin/reolink_pull.sh
  2) Ensure linger is enabled for background user timers:
       sudo loginctl enable-linger $USER
EOM
