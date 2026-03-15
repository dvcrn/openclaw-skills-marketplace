# ShrimpCard Field Requirements

Required fields
- schema_version: must be "1.0"
- card_id: short ID string
- name: lobster/shrimp name
- tagline: one-line expression
- description: short paragraph
- top_skills: exactly 3 capability tags chosen by OpenClaw (not necessarily most-used skills)
- owner.name: owner display name
- lobster_image_desc: must describe a lobster/shrimp image

Optional fields
- owner.contact: contact string
- image.url or image.data_url: main image
- image.placeholder: set to "image" if no image
- qr.url or qr.data_url
- theme: background, border, accent, tag_colors

Style notes
- Keep title <= 12 chars if possible
- Keep tagline <= 40 chars if possible
- Keep description <= 50 chars if possible
- Tags should be short and action-oriented

Image generation prompt reference
Use this as a starting point. Replace fields with actual card content and ensure QR is captured and composited.

**Style:** A premium 2D digital illustration of an AI agent character card. The visual style is a direct fusion of retro-modern graphic design and vibrant comic illustration. Use bold, clean black outlines and a halftone dot texture for a vintage print feel.

**Color Palette:** Vibrant Coral-Orange (#FF7043), Deep Teal (#008080), and a warm Cream background (#FFFDD0).

**Card Structure (Strictly following the layout):**
1. **Header Illustration (Top):** Inside a rounded rectangular frame, a detailed and expressive character illustration of a spicy lobster in a busy office setting, surrounded by floating digital screens, chat bubbles, and coffee mugs.
2. **Identity Section (Below Image):** Main Title in bold thick sans-serif black typography. Secondary Text (ID) in smaller clean monospace.
3. **Biography Section:** A neat block of centered Chinese text with generous line spacing.
4. **Skills Row:** A horizontal row of three pill-shaped buttons with thin black outlines.
5. **Footer Section (Bottom):** Left side: owner text. Right side: a rounded white square containing a QR code and a minimalist logo.

**QR requirement:** The QR must be captured from user input and composited into the footer square. If no QR is provided, keep the square empty.
