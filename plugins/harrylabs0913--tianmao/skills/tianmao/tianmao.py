#!/usr/bin/env python3
"""
Tianmao (天猫) CLI Tool
Simple browser launcher for Tmall.com e-commerce platform.

Usage:
    tianmao open          - Open Tmall homepage (https://www.tmall.com)
    tianmao tianmao       - Open alternative domain (https://www.tianmao.com)
    tianmao help          - Show this help message
    tianmao version       - Show version information
"""

import sys
import subprocess
import platform

VERSION = "1.0.0"

# Tmall URLs
TMALL_URL = "https://www.tmall.com"
TIANMAO_URL = "https://www.tianmao.com"


def open_browser(url: str) -> None:
    """
    Open the given URL in the default browser.
    Uses different methods depending on the operating system.
    """
    system = platform.system()
    
    try:
        if system == "Darwin":
            # macOS: use 'open' command
            subprocess.run(["open", url], check=True)
        elif system == "Linux":
            # Linux: try xdg-open first, then fall back to other methods
            try:
                subprocess.run(["xdg-open", url], check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback: try to detect the browser
                for browser in ["google-chrome", "chromium", "firefox", "brave"]:
                    try:
                        subprocess.run([browser, url], check=True)
                        return
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                print("Error: Could not find a browser to open. Please install Chrome, Firefox, or Chromium.")
                sys.exit(1)
        elif system == "Windows":
            # Windows: use 'start' command via cmd
            subprocess.run(["cmd", "/c", "start", url], check=True, shell=True)
        else:
            # Fallback: try to use webbrowser module
            import webbrowser
            webbrowser.open(url)
    except Exception as e:
        print(f"Error opening browser: {e}")
        sys.exit(1)


def show_help() -> None:
    """Display help information."""
    help_text = """
Tianmao (天猫) CLI Tool - Simple browser launcher for Tmall.com

Usage:
    tianmao open          Open Tmall homepage (https://www.tmall.com)
    tianmao tianmao       Open alternative domain (https://www.tianmao.com)
    tianmao help          Show this help message
    tianmao version       Show version information

Description:
    This tool helps you quickly open the Tmall (天猫) website in your browser.
    It's designed to be a simple, no-frills utility that guides users to the
    correct Tmall URLs and lets them browse, shop, and complete transactions
    independently.

Privacy & Security:
    - No authentication is handled by this tool
    - No data or cookies are stored
    - All interaction happens in your own browser session
    - Users see exactly what URL is opened

Examples:
    $ tianmao open
    # Opens https://www.tmall.com in your default browser

    $ tianmao tianmao
    # Opens https://www.tianmao.com in your default browser
"""
    print(help_text)


def show_version() -> None:
    """Display version information."""
    print(f"Tianmao (天猫) CLI Tool v{VERSION}")
    print("Simple browser launcher for Tmall.com e-commerce platform")
    print("Maintainer: OpenClaw Skills Team")


def main() -> None:
    """Main entry point for the CLI."""
    if len(sys.argv) < 2:
        print("Error: No command specified.")
        print("\nUsage: tianmao <command>")
        print("Run 'tianmao help' for more information.")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "open":
        print(f"Opening Tmall homepage: {TMALL_URL}")
        open_browser(TMALL_URL)
        print("Browser opened. Happy shopping!")
    elif command == "tianmao":
        print(f"Opening Tmall alternative domain: {TIANMAO_URL}")
        open_browser(TIANMAO_URL)
        print("Browser opened. Happy shopping!")
    elif command in ("help", "--help", "-h"):
        show_help()
    elif command in ("version", "--version", "-v"):
        show_version()
    else:
        print(f"Error: Unknown command '{command}'")
        print("\nUsage: tianmao <command>")
        print("Run 'tianmao help' for more information.")
        sys.exit(1)


if __name__ == "__main__":
    main()
