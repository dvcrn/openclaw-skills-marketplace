# Tianmao (天猫) CLI Tool

Simple browser launcher for Tmall.com (天猫) e-commerce platform.

## Description

This tool helps you quickly open the Tmall (天猫) website in your browser. It's designed to be a simple, no-frills utility that guides users to the correct Tmall URLs and lets them browse, shop, and complete transactions independently.

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/harrylabs0913/tianmao.git
cd tianmao

# Make the script executable
chmod +x tianmao.py

# Optional: Create a symlink for global access
ln -s $(pwd)/tianmao.py /usr/local/bin/tianmao
```

## Usage

```bash
# Open Tmall homepage
tianmao open

# Open alternative domain (tianmao.com)
tianmao tianmao

# Show help
tianmao help

# Show version
tianmao version
```

## Commands

| Command | Description |
|---------|-------------|
| `open` | Open Tmall homepage (https://www.tmall.com) |
| `tianmao` | Open alternative domain (https://www.tianmao.com) |
| `help` | Show help message |
| `version` | Show version information |

## Features

- ✅ **Simple Launch**: Just opens the browser to Tmall – no complex setup
- ✅ **Dual Domain Support**: Supports both tmall.com and tianmao.com URLs
- ✅ **User Control**: After opening the browser, users complete all shopping independently
- ✅ **No Data Collection**: Does not store any user data, cookies, or browsing history
- ✅ **Cross-Platform**: Works on macOS, Linux, and Windows

## Privacy & Security

- **No Authentication**: This tool does not handle login or authentication
- **No Data Storage**: No cookies, browsing history, or personal data is stored
- **Browser-Only**: All interaction happens in the user's own browser session
- **Transparent**: Users see exactly what URL is opened and can verify it's the legitimate Tmall site

## Requirements

- Python 3.6 or higher
- A modern web browser (Chrome, Firefox, Safari, Edge, etc.)

## Supported Platforms

- macOS
- Linux
- Windows

## Why This Tool Exists

Many users know they want to shop on "天猫" but may not remember the exact URL (tmall.com vs tianmao.com). This tool provides a quick, reliable way to get to the right starting point, then steps out of the way so users can shop normally.

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues, please file an issue on GitHub:
https://github.com/harrylabs0913/tianmao/issues
