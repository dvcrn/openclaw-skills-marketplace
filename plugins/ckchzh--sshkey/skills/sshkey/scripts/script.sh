#!/bin/bash
SSH_DIR="$HOME/.ssh"
cmd_generate() { local name="${1:-id_ed25519}" type="${2:-ed25519}"
    local keyfile="$SSH_DIR/$name"
    [ -f "$keyfile" ] && { echo "Key already exists: $keyfile"; echo "Use a different name."; return 1; }
    mkdir -p "$SSH_DIR" && chmod 700 "$SSH_DIR"
    ssh-keygen -t "$type" -f "$keyfile" -N "" -C "$(whoami)@$(hostname)-$(date +%Y%m%d)"
    echo ""; echo "Public key:"; cat "${keyfile}.pub"
}
cmd_list() { echo "=== SSH Keys in $SSH_DIR ===" 
    ls -la "$SSH_DIR"/*.pub 2>/dev/null || echo "No public keys found"
    echo ""; echo "Private keys:"
    for f in "$SSH_DIR"/id_*; do
        [ -f "$f" ] && [[ ! "$f" == *.pub ]] && echo "  $f ($(ssh-keygen -lf "$f" 2>/dev/null | awk '{print $2}'))"
    done
}
cmd_fingerprint() { local key="${1:-$SSH_DIR/id_ed25519.pub}"
    [ ! -f "$key" ] && key="${key}.pub"
    [ ! -f "$key" ] && { echo "Key not found: $key"; return 1; }
    ssh-keygen -lf "$key" 2>/dev/null
}
cmd_copy() { local key="${1:-$SSH_DIR/id_ed25519.pub}"
    [ ! -f "$key" ] && key="$SSH_DIR/id_rsa.pub"
    [ ! -f "$key" ] && { echo "No public key found. Generate one: sshkey generate"; return 1; }
    echo "=== Public Key (copy this) ==="
    cat "$key"
}
cmd_test() { local host="$1"; [ -z "$host" ] && { echo "Usage: sshkey test <host>"; return 1; }
    echo "Testing SSH to $host..."
    ssh -o ConnectTimeout=5 -o BatchMode=yes -T "$host" 2>&1 | head -5
}
cmd_help() { echo "SSHKey - SSH Key Manager"; echo "Commands: generate [name] [type] | list | fingerprint [key] | copy [key] | test <host> | help"; }
cmd_info() { echo "SSHKey v1.0.0 | Powered by BytesAgain"; }
case "$1" in generate) shift; cmd_generate "$@";; list) cmd_list;; fingerprint) shift; cmd_fingerprint "$@";; copy) shift; cmd_copy "$@";; test) shift; cmd_test "$@";; info) cmd_info;; help|"") cmd_help;; *) cmd_help; exit 1;; esac
