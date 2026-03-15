# Basic Usage Examples

## As an OpenClaw Agent

When the Tianmao skill is installed, agents can use it to open Tmall for users:

1. **Direct invocation by name** (if the agent recognizes the skill):
   ```
   User: "帮我打开天猫"
   Agent: (invokes tianmao open)
   ```

2. **Manual browser tool usage** (fallback):
   ```javascript
   browser({action: 'open', url: 'https://www.tmall.com', profile: 'chrome'})
   ```

## As a Standalone CLI

### Installation
Make the script executable and add it to your PATH:

```bash
# Option 1: Symlink to a directory in your PATH
ln -s ~/.openclaw/workspace/skills/tianmao/bin/tianmao /usr/local/bin/

# Option 2: Add the bin directory to PATH
export PATH="$PATH:~/.openclaw/workspace/skills/tianmao/bin"
```

### Basic Commands
```bash
# Open Tmall homepage
tianmao open

# Open Tianmao (alternative domain)
tianmao tianmao

# Show help
tianmao help

# Show version
tianmao version
```

### Integration with Shell Aliases
Add to your `~/.bashrc` or `~/.zshrc`:
```bash
alias tmall="tianmao open"
alias tianmao="tianmao tianmao"
```

## Common Use Cases

### Quick Shopping Session
```bash
# Want to browse Tmall quickly?
tianmao open
# Browser opens, you can start shopping immediately
```

### Teaching Someone How to Access Tmall
```bash
# For users who know "天猫" but not the exact URL:
tianmao tianmao
# Opens tianmao.com (which redirects to tmall.com)
```

### Scripting & Automation
```bash
# Open Tmall as part of a larger workflow
tianmao open &
# Continue with other tasks while browser loads
```

## Troubleshooting

### Browser Doesn't Open
- **macOS**: Ensure `open` command is available (default)
- **Linux**: Install `xdg-utils` package: `sudo apt install xdg-utils`
- **Windows**: Should work with `start` command in Git Bash or WSL

### Command Not Found
- Ensure the script is executable: `chmod +x ~/.openclaw/workspace/skills/tianmao/bin/tianmao`
- Check PATH: `echo $PATH` should include the directory containing `tianmao`

### Wrong URL Opens
- Verify the URL: Tmall uses `https://www.tmall.com`
- Alternative: `https://www.tianmao.com` redirects to the main site
- If using a VPN or in China, you might be redirected to the regional version