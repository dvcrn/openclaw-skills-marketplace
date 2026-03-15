# Plume Image Skill Usage Examples

## Text-to-Image (Most Common Scenario)

```bash
# 1. Create a text-to-image task
python3 scripts/process_image.py create \
  --category "banana" \
  --prompt "a cute orange cat sitting on a windowsill, afternoon sunlight, photorealistic" \
  --processing-mode "text_to_image" \
  --image-size "1K" \
  --aspect-ratio "1:1"

# Output: {"success": true, "task_id": 123, "status": 1, "credits_cost": 10}

# 2. Poll and wait for result
python3 scripts/process_image.py poll --task-id 123

# Output: {"success": true, "status": 3, "result_url": "https://r2.../result.jpg", ...}

# 3. Deliver to Feishu
python3 scripts/process_image.py deliver \
  --result-url "https://r2.../result.jpg" \
  --chat-id "oc_xxxxx" \
  --chat-type "group"
```

## Image-to-Image (User Sent a Reference Image)

```bash
# 1. Transfer Feishu image to R2
python3 scripts/process_image.py transfer \
  --image-key "img_v3_xxx"

# Output: {"success": true, "image_url": "https://r2.../transferred.jpg", ...}

# 2. Create image-to-image task
python3 scripts/process_image.py create \
  --category "banana" \
  --prompt "transform into watercolor painting style" \
  --image-url "https://r2.../transferred.jpg" \
  --processing-mode "image_to_image"

# 3. Poll + deliver (same as text-to-image)
```

## Background Removal

```bash
# 1. Transfer image (if from Feishu)
python3 scripts/process_image.py transfer --image-key "img_v3_xxx"

# 2. Create background removal task (no processing-mode or prompt needed)
python3 scripts/process_image.py create \
  --category "remove-bg" \
  --image-url "https://r2.../photo.jpg"

# 3. Poll + deliver
```

## Using Doubao Seedream (Supports Chinese Prompts)

```bash
python3 scripts/process_image.py create \
  --category "seedream" \
  --prompt "a cute Shiba Inu wearing a spacesuit walking on the moon" \
  --processing-mode "text_to_image" \
  --image-size "2K"
```

## HD 4K Image

```bash
python3 scripts/process_image.py create \
  --category "banana" \
  --prompt "a stunning landscape photograph" \
  --processing-mode "text_to_image" \
  --image-size "4K" \
  --aspect-ratio "16:9"
```

## Associate with Project

```bash
python3 scripts/manage_project.py create-with-project \
  --category "banana" \
  --prompt "a beautiful landscape" \
  --processing-mode "text_to_image" \
  --project-id "auto"
```

## Agent Complete Workflow Example

Typical processing flow when the Agent receives a user message:

### User says: "Generate a cat image for me"
```
1. Agent analyzes: text-to-image request, choose category=banana
2. Translate prompt: "a cute cat, detailed fur, soft lighting"
3. Execute create(processing-mode=text_to_image) → poll → deliver
```

### User sent an image, then says: "Remove the background"
```
1. Agent finds image_key from context
2. Execute transfer → create(category=remove-bg) → poll → deliver
```

### User sent an image, then says: "Convert this to oil painting style"
```
1. Agent finds image_key from context
2. Execute transfer → create(category=banana, processing-mode=image_to_image) → poll → deliver
```
