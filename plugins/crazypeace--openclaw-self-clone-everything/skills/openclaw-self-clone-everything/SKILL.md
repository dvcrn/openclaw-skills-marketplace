---
name: openclaw-self-clone-everything
description: "Clone and deploy OpenClaw to a new VPS. Use when you need to install OpenClaw on a fresh remote server via SSH. Steps: (1) Verify SSH access (IP, user, password/key), (2) Install OpenClaw via official non-interactive script, (3) Copy ~/.openclaw data, (4) Prompt to update credentials (e.g., Telegram bot token)."
---

# OpenClaw Clone to New VPS

Overview: Deploy OpenClaw to a new VPS using SSH and a non-interactive installer, then copy your ~/.opencl workspace and verify/update credentials.

## Prerequisites

- SSH access to the new VPS: IP address, username, and password (or SSH key)
- The new VPS runs a supported Linux distribution (verify with the official docs)
- Ensure outbound connectivity on the new VPS (to fetch the installer)

- Security: When prompted for passwords, avoid hardcoding them; prefer password prompts or SSH key-based auth.

## Procedure

### Step 1: Verify SSH connectivity

- Test access from the current environment to the new VPS.
- Example (interactive login test):
  ```bash
  ssh USER@VPS_IP
  ```
- Replace `USER` with the provided username and `VPS_IP` with the target IP.
- Exit the test SSH session once verified.

If auth uses an SSH key, ensure the private key is available and permissions are tightened (e.g., 600).

### Step 2: Install OpenClaw via non-interactive script

- Run the official installer in non-interactive mode on the new VPS:
  ```bash
  ssh USER@VPS_IP 'bash -c "$(curl -fsSL https://openclaw.ai/install.sh)" -- --no-onboard'
  ```
- Explanation:
  - `--no-onboard` skips the interactive onboarding wizard.
  - This command performs the installation over SSH without prompting.

If the new VPS blocks curl or `https://openclaw.ai`, download the installer locally and scp/transfer it before running `bash install.sh -- --no-onboard`.

### Step 3: Copy ~/.openclaw from the source to the new VPS

- Source path (current environment): `~/.openclaw`
- Target directory on the new VPS: `~/.openclaw`

- Create a compressed archive, transfer it, and extract on the new VPS:
  ```bash
  # Compress (on source)
  cd ~ && tar czf openclaw-data.tar.gz --exclude='*.log' --exclude='cache' --exclude='node_modules/.cache' .openclaw

  # Transfer
  scp openclaw-data.tar.gz USER@VPS_IP:~/

  # Extract (on new VPS)
  ssh USER@VPS_IP 'rm -rf ~/.openclaw && tar xzf ~/openclaw-data.tar.gz -C ~/'

  # Cleanup (optional, on both sides)
  rm openclaw-data.tar.gz
  ssh USER@VPS_IP 'rm ~/openclaw-data.tar.gz'
  ```

Notes and cautions:

- Review the contents you intend to copy. Avoid copying local temporary files or caches that should not be restored on the target.
- The example excludes `*.log`, `cache`, and `node_modules/.cache` to reduce archive size; adjust based on your directory layout.
- No ongoing synchronization; this is a one-time transfer.

### Step 4: Update or validate key credentials on the new VPS (Optional)

- Ask the user: "Do you want to update credentials on the new VPS? (e.g., Telegram bot token, API keys)"
- If user responds with "no" or "skip", skip this step and proceed to Step 5.
- If user responds with "yes" or wants to update, inspect and update sensitive settings in the new `~/.openclaw` directory:
  - Telegram bot tokens and API keys (e.g., `~/.openclaw/config.*` or environment files)
  - Provider credentials (if any), webhooks, and service URLs

Where to find credentials:

- Check `~/.openclaw/config` or related config files for tokens or service identifiers.
- Refer to provider-specific configuration files or environment settings.

### Step 5: Optional: Restart or reload OpenClaw on the new VPS

- ⚠️ This step restarts the OpenClaw service on the NEW VPS, not your current environment
- Reload or restart the OpenClaw service on the new VPS as needed:
  ```bash
  ssh USER@VPS_IP 'sudo systemctl restart openclaw || openclaw restart || echo "Restart manually per your system"'
  ```
- Verify by checking logs or by accessing the OpenClaw web UI (if exposed).

## Post-install checks

- Confirm the new VPS runs OpenClaw:
  - Check service status (e.g., `ssh USER@VPS_IP 'sudo systemctl status openclaw'`).
  - Review logs for errors (`ssh USER@VPS_IP 'journalctl -u openclaw -n 50'` or relevant log path).
- Validate that workspaces and agents appear correctly from `~/.openclaw`.
- Test provider/telebot connectivity with a simple request or health check.

## Security and hygiene

- Rotate freshly provisioned credentials or tokens that are environment-specific.
- Restrict SSH access: disable password auth, use key-based auth, configure firewall rules, and limit which users can SSH.
- Keep OpenClaw up to date on both source and target.

## Troubleshooting

- Installer fails over SSH:
  - Verify outbound connectivity and required tools (curl/bash).
  - Check the official docs for an alternative installation methods.
- rsync errors:
  - Ensure the target directory exists and permissions allow writes.
  - Reduce verbosity flags if needed to isolate issues.
- Credentials mismatch:
  - Compare token/secret values and update them on the new VPS.
  - Avoid committing secrets to version control; use environment variables or secrets management.
