# example for :
```bash
## Request
curl --location --request POST 'https://api.qnaigc.com/queue/fal-ai/kling-image/o1' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
    "prompt": "一只可爱的橘猫在阳光下打盹",
    "num_images": 2,
    "resolution": "2K",
    "aspect_ratio": "16:9"
}'

## Response

{
    "status": "IN_QUEUE",
    "request_id": "qimage-root-1770199726278452760",
    "response_url": "https://api.qnaigc.com/queue/fal-ai/kling-image/requests/qimage-root-1770199726278452760",
    "status_url": "https://api.qnaigc.com/queue/fal-ai/kling-image/requests/qimage-root-1770199726278452760/status",
    "cancel_url": ""
}

```

# example for : gemini-2.5-flash-image

```bash
## Request

curl --location --request POST 'https://api.qnaigc.com/v1/images/edits' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
    "model": "gemini-2.5-flash-image",
    "image": "https://aitoken-public.qnaigc.com/example/generate-video/running-man.jpg",
    "prompt": "为这个场景添加日落效果，让整体色调更温暖"
}'

## Response

{
    "created": 1234567890,
    "data": [
        {
            "b64_json": "iVBORw0KGgoAAAANSUhEUgA..."
        }
    ],
    "output_format": "png",
    "usage": {
        "total_tokens": 5234,
        "input_tokens": 1234,
        "output_tokens": 4000,
        "input_tokens_details": {
            "text_tokens": 234,
            "image_tokens": 1000
        }
    }
}
```

# example for : gemini-3.0-pro-image-preview
```bash
## Request

curl --location --request POST 'https://api.qnaigc.com/v1/images/edits' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
    "model": "gemini-3.0-pro-image-preview",
    "image": "https://aitoken-public.qnaigc.com/example/generate-video/running-man.jpg",
    "prompt": "为这个场景添加日落效果，让整体色调更温暖"
}'


# Response

{
    "created": 1234567890,
    "data": [
        {
            "b64_json": "iVBORw0KGgoAAAANSUhEUgA..."
        }
    ],
    "output_format": "png",
    "usage": {
        "total_tokens": 6234,
        "input_tokens": 1234,
        "output_tokens": 5000,
        "input_tokens_details": {
            "text_tokens": 234,
            "image_tokens": 1000
        }
    }
}
```
