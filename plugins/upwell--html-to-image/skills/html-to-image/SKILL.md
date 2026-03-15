---
name: html_to_image
description: "Takes a URL, HTML file path, or raw HTML code and generates a printable image."
---

# HTML to Image Skill (via agent-browser)

This skill utilizes OpenClaw's `agent-browser` composition to render a URL, local HTML file, or raw HTML string into an image. It executes a lightweight Bash script wrapper.

## Usage Guide
When using this skill to generate an image, provide the `source_type` and `source_content`.

- **source_type**: The content format (`url`, `file`, or `code`).
- **source_content**: The target URL, absolute file path, or HTML code block.
- **format**: The desired image format (`png`, `jpeg`, or `webp`). Default is `png`.
- **width**: The width of the browser viewport. Default is 1200px.
- **full_page**: Set to `true` to take a full page screenshot instead of just the viewport.
