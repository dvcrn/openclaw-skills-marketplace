---
name: seedream-image-generation
description: "Image generation via Volcengine Seedream API. Use this when you need to perform Text-to-Image (T2I), Image-to-Image (I2I),使用豆包生图 or general visual creative tasks based on textual or visual inputs."
---

# Seedream Image Generation Skill

This skill provides methods for calling the Volcengine Ark large model service platform's image generation models (Seedream).

## Select Environment

The script provides implementations for both Python and JavaScript:
- If your runtime is primarily Node.js/TypeScript or a web module, use **seedream.js**.
- If your runtime involves complex data analysis, batch scheduling, or is purely Python, use **seedream.py**.

## Supported Model Parameters (Model ID/Endpoint ID)

When invoking, the `model` parameter needs to be the deployment Endpoint ID from the Ark console (e.g., `ep-202X...`), which must be backed by one of the following foundational image generation models:
- `doubao-seedream-5-0-260128`
- `doubao-seedream-4-5-251128`
- `doubao-seedream-4-0-250828`

## Script Parameters

You must pass specific parameters to control the image generation. The available parameters are:

- **model** *(string, optional)*: Endpoint ID corresponding to the model. Defaults to `doubao-seedream-5-0-260128`.
- **prompt** *(string, required)*: Text description used to generate the image.
- **image** *(string | list of strings, optional)*: Local image path or image path list used for image-to-image generation. The scripts will read the local file, convert it to base64, and send it as the request `image` field.
- **watermark** *(boolean, optional)*: Whether to add a Volcengine AI watermark. Unprovided value assumes `false`.
- **optimize_prompt_options** *(object, optional)*: Configure automatic prompt optimization options. Format: JSON object. E.g., `{"mode": "standard"}`.
- **tools** *(list of objects, optional)*: Capabilities options for the model, formatted as JSON. Example: `[{"type": "web_search"}]`.
- **output_format** *(string, optional)*: The output image format. Options include `png`, `jpeg`.
- **sequential_image_generation** *(string, optional)*: Sequential image generation strategy (e.g., `"auto"`).
- **download_dir** *(string, optional)*: Local directory to save the generated images. If not provided, images will not be downloaded locally, and only the API response will be returned.

## Recommended width and height values

| Resolution | Aspect Ratio | Dimensions |
| :--------- | :----------- | :--------- |
| **2K**     | 1:1          | 2048x2048  |
|            | 4:3          | 2304x1728  |
|            | 3:4          | 1728x2304  |
|            | 16:9         | 2848x1600  |
|            | 9:16         | 1600x2848  |
|            | 3:2          | 2496x1664  |
|            | 2:3          | 1664x2496  |
|            | 21:9         | 3136x1344  |
| **3K**     | 1:1          | 3072x3072  |
|            | 4:3          | 3456x2592  |
|            | 3:4          | 2592x3456  |
|            | 16:9         | 4096x2304  |
|            | 9:16         | 2304x4096  |
|            | 2:3          | 2496x3744  |
|            | 3:2          | 3744x2496  |
|            | 21:9         | 4704x2016  |

## Usage Examples

**Python Example:**
```bash
cd <current_skill_dir>
python3 seedream.py \
  --prompt "A cute orange cat laying under the sun" \
  --model "ep-xxxxx..." \
  --size "1024x1024" \
  --watermark "false" \
  --output_format "png"
```

**Node.js Example:**
```bash
cd <current_skill_dir>
node seedream.js \
  --prompt "A cute orange cat laying under the sun" \
  --model "ep-xxxxx..." \
  --size "1024x1024" \
  --watermark "false" \
  --output_format "png"
```

**Image-to-Image Example (Python):**
```bash
cd <current_skill_dir>
python3 seedream.py \
  --prompt "Turn this product photo into a clean white-background ecommerce image" \
  --image "/path/to/source.png" \
  --model "ep-xxxxx..."
```

**Advanced Example with Tools and Optimization (Python):**
```bash
cd <current_skill_dir>
python3 seedream.py \
  --prompt "A futuristic cityscape" \
  --model "ep-xxxxx..." \
  --optimize_prompt_options '{"mode": "standard"}' \
  --tools '[{"type": "web_search"}]'
```

For more detailed API documentation, please visit: [https://www.volcengine.com/docs/82379/1541523?lang=zh](https://www.volcengine.com/docs/82379/1541523?lang=zh)
For more model id list or check the newest model id if required, please visit: [https://www.volcengine.com/docs/82379/1330310?lang=zh#36969059](https://www.volcengine.com/docs/82379/1330310?lang=zh#36969059), and then update this seedream-image-generation/SKILL.md file "Supported Model Parameters".