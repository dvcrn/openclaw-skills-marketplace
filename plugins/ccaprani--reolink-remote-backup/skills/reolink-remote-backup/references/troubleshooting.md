# Reolink Remote Backup Troubleshooting

## Symptoms and fixes

## 1) `vsftpd` fails to start (`status=2/INVALIDARGUMENT`)

- Run parser directly:
  - `/usr/sbin/vsftpd /etc/vsftpd.conf`
- Remove unsupported config keys reported by OOPS message.
- Restart: `systemctl restart vsftpd`

## 2) Camera FTP test shows `451 login failed`

- Re-enter username/password in app.
- Reset server password: `passwd reolinkftp`.
- Ensure user in allow list:
  - `echo reolinkftp >/etc/vsftpd.userlist`
- Check logs:
  - `tail -n 120 /var/log/vsftpd.log`
  - `tail -n 120 /var/log/auth.log`

## 3) Camera FTP test shows `455` failure

Usually write/path/passive/TLS mismatch.

- Confirm writable ingest path:
  - `mkdir -p /srv/reolink/incoming`
  - `chown -R reolinkftp:reolinkftp /srv/reolink`
  - `chmod 775 /srv/reolink/incoming`
- Confirm passive ports open (21 + 50000-50100/TCP).
- Temporarily disable forced TLS for debugging only:
  - `force_local_logins_ssl=NO`
  - `force_local_data_ssl=NO`

## 4) Connect appears in logs, but no USER/PASS lines

Likely protocol mismatch or early TLS negotiation failure.

- Enable protocol logging in vsftpd config:
  - `log_ftp_protocol=YES`
  - `dual_log_enable=YES`
- Re-test and inspect `/var/log/vsftpd.log`.

## 5) Local pull script says mount missing

- Verify mount:
  - `findmnt <mountpoint>`
  - `mount | grep <name>`
- Check duplicate/conflicting `/etc/fstab` entries.
- Run:
  - `sudo systemctl daemon-reload`
  - `sudo mount -a`

## 6) Nothing arrives while camera is remote and idle

- Trigger uploads may require motion/events.
- Use camera app/web test button if available.
- Historical microSD archives may need explicit download through Reolink web/app tools.

## 7) VPS fills up

- Confirm local pull timer active:
  - `systemctl --user list-timers | grep reolink-pull`
- Confirm local script ran and logs are fresh.
- Keep VPS retention prune enabled.
