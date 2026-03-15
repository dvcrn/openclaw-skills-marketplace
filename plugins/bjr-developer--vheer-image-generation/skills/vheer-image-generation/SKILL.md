---
name: vheer-image-generation
description: "Vheer Free AI Image Generation Scripts"
---

# Vheer Automation Skill

Automated image generation using Vheer.com's browser interface.

## 🌟 Overview
This skill leverages **Playwright** to automate the text-to-image generation process on Vheer.com. It interacts directly with the web interface, avoiding the need for manual cookie management or complex API reverse-engineering.

## 🛠 Features
- **Headless Generation**: Run in the background or in visible mode.
- **Dynamic Prompts**: Pass any prompt via the command line.
- **Automatic Output**: Saves the resulting image directly to your local machine.
- **Persistent Sessions**: Support for User Data Directories to keep you logged in.

## 🚀 Usage

### 1. Installation
Ensure you have the required dependencies installed:
```bash
python3 -m pip install playwright
playwright install chromium
```

### 2. Generating an Image
Run the script with your desired prompt:
```bash
python3 scripts/vheer_automation.py "A majestic phoenix rising from the ashes, cinematic lighting"
```

### 3. CLI Options
- `-o`, `--output`: Specify the output filename (default: `vheer_output.png`).
- `--headful`: Run browser in visible mode (useful for debugging).
- `--user-data`: Path to a browser profile directory (keeps you logged in).

## 📂 Project Structure
- `scripts/vheer_automation.py`: The single, unified automation script.
- `vheer_output.png`: The default location for generated images.

## 💡 How it Works
The script launches a Chromium instance, navigates to the Vheer text-to-image application, fills the prompt textarea, and triggers the generation. Once the "Processing..." state completes, it takes an element-level screenshot of the final image to bypass `blob:` URL limitations.
