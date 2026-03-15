#!/bin/bash
# setup-tailscale.sh - Configura Tailscale para servir o Auth Server
# Execute: chmod +x setup-tailscale.sh && ./setup-tailscale.sh

set -e

AUTH_PORT=8456

echo "🔐 Max Auth - Setup"
echo "==================="

# Verificar se Tailscale está instalado
if ! command -v tailscale &> /dev/null; then
  echo "❌ Tailscale não encontrado. Instale primeiro:"
  echo "   curl -fsSL https://tailscale.com/install.sh | sh"
  exit 1
fi

echo "✓ Tailscale encontrado"

# Verificar se está logado no Tailscale
if ! tailscale status &> /dev/null; then
  echo "❌ Tailscale não está conectado. Execute: sudo tailscale up"
  exit 1
fi

echo "✓ Tailscale conectado"

# Verificar se auth-server.js existe
if [ ! -f "$HOME/.max-auth/auth-server.js" ]; then
  echo "❌ auth-server.js não encontrado em ~/.max-auth/"
  exit 1
fi

echo "✓ auth-server.js encontrado"

# Criar serviço systemd
SERVICE_FILE="/etc/systemd/system/max-auth.service"

sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Max Auth Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/.max-auth
ExecStart=/usr/bin/node $HOME/.max-auth/auth-server.js
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Serviço systemd criado"

echo ""
echo "🚀 Próximos passos:"
echo "==================="
echo ""
echo "1. Defina sua senha mestra (SUBSTITUA 'sua_senha_aqui'):"
echo "   cd ~/.max-auth && node auth-server.js set-password 'sua_senha_aqui'"
echo ""
echo "2. Inicie o serviço:"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable max-auth"
echo "   sudo systemctl start max-auth"
echo ""
echo "3. Configure o Tailscale serve:"
echo "   sudo tailscale serve --https=443 --bg http://localhost:$AUTH_PORT"
echo ""
echo "4. Acesse:"
TS_HOSTNAME=$(tailscale status --json 2>/dev/null | grep -o '"DNSName":"[^"]*"' | head -1 | cut -d'"' -f4)
if [ -n "$TS_HOSTNAME" ]; then
  echo "   https://${TS_HOSTNAME}auth"
else
  echo "   https://<seu-hostname-tailscale>/auth"
fi
echo ""
echo "📋 Comandos úteis:"
echo "   Status:  node auth-server.js status"
echo "   Logs:    sudo journalctl -u max-auth -f"
echo "   Restart: sudo systemctl restart max-auth"
echo ""
