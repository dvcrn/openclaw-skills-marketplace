---
name: wifi-qr
description: "Generate QR code for Wi-Fi credentials"
---

# Wi-Fi QR

Generate a QR code for Wi-Fi credentials. Scan the QR code with a phone to instantly connect to the network without typing the password.

## Commands

```bash
# Generate a QR code for a Wi-Fi network (defaults to WPA)
wifi-qr "MyNetwork" "mypassword"

# Specify the security type explicitly
wifi-qr "MyNetwork" "mypassword" --type WPA
```

## Install

```bash
sudo dnf install qrencode
```
