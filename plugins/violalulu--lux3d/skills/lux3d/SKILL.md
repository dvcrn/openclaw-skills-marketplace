---
name: lux3d
description: "Use Lux3D to generate 3D models from 2D images. Trigger conditions: when user asks to generate 3D model from image, image to 3D, convert image to 3D object, create 3D from photo, or any request involving 2D-to-3D conversion."
---

## What is Lux3D
Lux3D is a multimodal 3D generation model developed by Manycore Technology. It converts 2D images into high-quality 3D PBR models that are perfectly compatible with QIZHEN Engine.

## How to Use

### 1. Get API Key
External users need to fill out a questionnaire to apply for an API key:
- Questionnaire: https://forms.cloud.microsoft.com/r/kRTjdDBV1e
- Or contact: lux3d@qunhemail.com

### 2. API Call Example

```python
import base64
import hashlib
import time
import requests
from PIL import Image
import os
import io

# Configuration
API_KEY = "your_lux3d_api_key"  # Replace with your API key
BASE_URL = "https://api.luxreal.ai"

def parse_invitation_code(code):
    """Parse base64 encoded invitation code to get ak/sk/appuid (format: version:ak:sk:appuid)"""
    decoded = base64.b64decode(code).decode('utf-8')
    parts = decoded.split(':')
    if len(parts) != 4:
        raise ValueError(f"Invalid invitation code format: expected 4 parts, got {len(parts)}")
    return {'version': parts[0], 'ak': parts[1], 'sk': parts[2], 'appuid': parts[3]}

def generate_sign(ak, sk, appuid):
    """Generate MD5 signature"""
    timestamp = str(int(time.time() * 1000))
    sign_string = sk + ak + appuid + timestamp
    sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest()
    return {'appkey': ak, 'appuid': appuid, 'timestamp': timestamp, 'sign': sign}

def image_to_base64(image_path):
    """Convert image file to base64"""
    img = Image.open(image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{img_str}"

def create_task(image_path):
    """Submit image-to-3D task"""
    # Parse API key
    code = parse_invitation_code(API_KEY)
    sign = generate_sign(code['ak'], code['sk'], code['appuid'])
    
    # Convert image to base64
    base64_image = image_to_base64(image_path)
    
    # Submit task
    url = f"{BASE_URL}/global/lux3d/generate/task/create?appuid={sign['appuid']}&appkey={sign['appkey']}&sign={sign['sign']}&timestamp={sign['timestamp']}"
    
    headers = {"Content-Type": "application/json"}
    payload = {"img": base64_image, "lux3dToken": API_KEY}
    
    response = requests.post(url, json=payload, headers=headers)
    try:
        result = response.json()
    except ValueError:
        raise Exception(f"Invalid JSON response: {response.text}")
    return result.get("d")  # task_id

def query_task_status(task_id):
    """Query task status and get result"""
    code = parse_invitation_code(API_KEY)
    sign = generate_sign(code['ak'], code['sk'], code['appuid'])
    
    url = f"{BASE_URL}/global/lux3d/generate/task/get?busid={task_id}&appuid={sign['appuid']}&appkey={sign['appkey']}&sign={sign['sign']}&timestamp={sign['timestamp']}"
    
    max_attempts = 60
    interval = 15
    
    for attempt in range(max_attempts):
        response = requests.get(url, headers={"Content-Type": "application/json"})
        try:
            result = response.json()
        except ValueError:
            raise Exception(f"Invalid JSON response: {response.text}")
        status = result.get("d", {}).get("status")
        
        if status == 3:  # Completed
            outputs = result.get("d", {}).get("outputs", [])
            if outputs:
                return outputs[0].get("content")  # GLB model URL
        elif status == 4:  # Failed
            raise Exception("Task execution failed")
        else:
            time.sleep(interval)
    
    raise Exception("Task timeout")

# Example usage
image_path = "path/to/your/image.jpg"

# Step 1: Submit task
print("=== Submitting task ===")
task_id = create_task(image_path)
print(f"Task ID: {task_id}")

# Step 2: Query result (wait for completion)
print("\n=== Querying result ===")
model_url = query_task_status(task_id)
print(f"Generated 3D model URL: {model_url}")

# Step 3: Download model
output_name = image_path.rsplit('.', 1)[0] + '_3d.zip'
print(f"\n=== Downloading model ===")
response = requests.get(model_url)
with open(output_name, 'wb') as f:
    f.write(response.content)
print(f"Downloaded: {output_name} ({len(response.content)} bytes)")
```

### 3. Batch Generation
To batch generate 3D assets from multiple images:

```python
import base64
import hashlib
import time
import requests
from PIL import Image
import os
import io

# Configuration
API_KEY = "your_lux3d_api_key"  # Replace with your API key
BASE_URL = "https://api.luxreal.ai"
IMAGE_DIR = "path/to/images"  # Replace with your image directory

def parse_invitation_code(code):
    """Parse base64 encoded invitation code (format: version:ak:sk:appuid)"""
    decoded = base64.b64decode(code).decode('utf-8')
    parts = decoded.split(':')
    if len(parts) != 4:
        raise ValueError(f"Invalid invitation code format: expected 4 parts, got {len(parts)}")
    return {'version': parts[0], 'ak': parts[1], 'sk': parts[2], 'appuid': parts[3]}

def generate_sign(ak, sk, appuid):
    timestamp = str(int(time.time() * 1000))
    sign_string = sk + ak + appuid + timestamp
    sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest()
    return {'appkey': ak, 'appuid': appuid, 'timestamp': timestamp, 'sign': sign}

def image_to_base64(image_path):
    img = Image.open(image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f'data:image/jpeg;base64,{img_str}'

def create_task(image_path):
    code = parse_invitation_code(API_KEY)
    sign = generate_sign(code['ak'], code['sk'], code['appuid'])
    base64_image = image_to_base64(image_path)
    
    url = f'{BASE_URL}/global/lux3d/generate/task/create?appuid={sign["appuid"]}&appkey={sign["appkey"]}&sign={sign["sign"]}&timestamp={sign["timestamp"]}'
    
    headers = {'Content-Type': 'application/json'}
    payload = {'img': base64_image, 'lux3dToken': API_KEY}
    
    response = requests.post(url, json=payload, headers=headers)
    try:
        result = response.json()
    except ValueError:
        raise Exception(f"Invalid JSON response: {response.text}")
    return result.get('d')

def query_task_status(task_id):
    code = parse_invitation_code(API_KEY)
    sign = generate_sign(code['ak'], code['sk'], code['appuid'])
    
    url = f'{BASE_URL}/global/lux3d/generate/task/get?busid={task_id}&appuid={sign["appuid"]}&appkey={sign["appkey"]}&sign={sign["sign"]}&timestamp={sign["timestamp"]}'
    
    max_attempts = 60
    interval = 15
    
    for attempt in range(max_attempts):
        response = requests.get(url, headers={'Content-Type': 'application/json'})
        try:
            result = response.json()
        except ValueError:
            raise Exception(f"Invalid JSON response: {response.text}")
        status = result.get('d', {}).get('status')
        
        if status == 3:
            outputs = result.get('d', {}).get('outputs', [])
            if outputs:
                return outputs[0].get('content')
        elif status == 4:
            raise Exception('Task execution failed')
        else:
            time.sleep(interval)
    
    raise Exception('Task timeout')

# Batch process - Submit one, poll, download immediately, then next (sequential with async download)
import threading

results = []
results_lock = threading.Lock()
pending_downloads = []  # [(filename, model_url), ...]
download_lock = threading.Lock()
download_pending = threading.Condition(download_lock)
done_submitting = False

def download_worker():
    """Background thread that downloads models as they become available"""
    while True:
        with download_lock:
            while len(pending_downloads) == 0:
                if done_submitting:
                    return
                download_pending.wait()
            if done_submitting and len(pending_downloads) == 0:
                return
            filename, model_url = pending_downloads.pop(0)
        
        output_name = filename.rsplit('.', 1)[0] + '_3d.zip'
        output_path = os.path.join(IMAGE_DIR, output_name)
        print(f'Downloading {filename}...')
        try:
            response = requests.get(model_url)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f'Downloaded: {output_name} ({len(response.content)} bytes)')
            with results_lock:
                results.append(f'{filename}: {model_url} -> {output_name}')
        except Exception as e:
            print(f'ERROR downloading {filename}: {e}')
            with results_lock:
                results.append(f'{filename}: ERROR - {e}')

# Start download worker thread
download_thread = threading.Thread(target=download_worker)
download_thread.start()

print("=== Processing images ===")
for filename in sorted(os.listdir(IMAGE_DIR)):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        image_path = os.path.join(IMAGE_DIR, filename)
        
        # Step 1: Submit task
        print(f'\n--- Processing: {filename} ---')
        print(f'Submitting task...')
        try:
            task_id = create_task(image_path)
            print(f'Task ID: {task_id}')
        except Exception as e:
            print(f'ERROR submitting task: {e}')
            with results_lock:
                results.append(f'{filename}: ERROR - {e}')
            continue
        
        # Step 2: Poll until complete
        print(f'Waiting for result...')
        try:
            model_url = query_task_status(task_id)
            print(f'Result: {model_url}')
        except Exception as e:
            print(f'ERROR: {e}')
            with results_lock:
                results.append(f'{filename}: ERROR - {e}')
            continue
        
        # Step 3: Queue download (async)
        with download_lock:
            pending_downloads.append((filename, model_url))
            download_pending.notify()

# Signal download worker we're done
done_submitting = True
with download_lock:
    download_pending.notify_all()

download_thread.join()

# Save results
print('\n=== Summary ===')
with open(os.path.join(IMAGE_DIR, 'results.txt'), 'w') as f:
    f.write('\n'.join(results))
for r in results:
    print(r)
```

### 4. Output Format
The generated model includes:
- White model GLB file
- 9 PBR material channel maps

## More Information
- GitHub: https://github.com/manycore-research/ComfyUI-Lux3D
- Email: lux3d@qunhemail.com
