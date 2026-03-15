#!/usr/bin/env python3
"""
Tomoviee AI - Text-to-Video API client
根据文本描述生成视频
"""

import base64
import json
import time
from typing import Dict, Optional, Any
import requests


class TomovieeText2VideoClient:
    """Text-to-Video API client for Tomoviee AI."""
    
    BASE_URL = "https://open-api.wondershare.cc/v1/open/capacity/application"
    RESULT_ENDPOINT = "https://open-api.wondershare.cc/v1/open/pub/task"
    ENDPOINT = "tm_text2video_b"
    
    def __init__(self, app_key: str, app_secret: str):
        """Initialize Text-to-Video API client."""
        self.app_key = app_key
        self.access_token = self._generate_token(app_key, app_secret)
    
    def _generate_token(self, app_key: str, app_secret: str) -> str:
        """Generate base64 access token."""
        credentials = f"{app_key}:{app_secret}"
        return base64.b64encode(credentials.encode()).decode()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        return {
            "Content-Type": "application/json",
            "X-App-Key": self.app_key,
            "Authorization": f"Basic {self.access_token}"
        }
    
    def _make_request(self, payload: Dict[str, Any]) -> str:
        """Make API request and return task_id."""
        url = f"{self.BASE_URL}/{self.ENDPOINT}"
        response = requests.post(url, headers=self._get_headers(), json=payload)
        result = response.json()
        
        if result.get("code") != 0:
            raise Exception(f"API Error: {result.get('msg', 'Unknown error')}")
        
        return result["data"]["task_id"]
    
    def text_to_video(
        self,
        prompt: str,
        resolution: str = "720p",
        duration: int = 5,
        aspect_ratio: str = "16:9",
        camera_move_index: Optional[int] = None,
        callback: Optional[str] = None,
        params: Optional[str] = None
    ) -> str:
        """
        Generate video from text description.
        
        Args:
            prompt: Text description (subject + action + scene + camera)
            resolution: Video resolution (720p or 1080p)
            duration: Video duration in seconds (only 5 supported)
            aspect_ratio: Video aspect ratio (16:9, 9:16, 4:3, 3:4, 1:1)
            camera_move_index: Optional camera movement type (1-46)
            callback: Optional callback URL
            params: Optional transparent parameters
            
        Returns:
            task_id for polling result
        """
        payload = {
            "prompt": prompt,
            "resolution": resolution,
            "duration": duration,
            "aspect_ratio": aspect_ratio
        }
        
        if camera_move_index is not None:
            payload["camera_move_index"] = camera_move_index
        if callback:
            payload["callback"] = callback
        if params:
            payload["params"] = params
        
        return self._make_request(payload)
    
    def get_result(self, task_id: str) -> Dict[str, Any]:
        """Get task result."""
        response = requests.post(
            self.RESULT_ENDPOINT,
            headers=self._get_headers(),
            json={"task_id": task_id}
        )
        
        result = response.json()
        
        if result.get("code") != 0 and not result.get("data"):
            raise Exception(f"API Error: {result.get('msg', 'Unknown error')}")
        
        return result["data"]
    
    def poll_until_complete(
        self,
        task_id: str,
        poll_interval: int = 10,
        timeout: int = 600
    ) -> Dict[str, Any]:
        """Poll task until completion or timeout."""
        elapsed = 0
        
        while elapsed < timeout:
            result = self.get_result(task_id)
            status = result["status"]
            
            # Status: 3=success, 4=failed, 5=cancelled, 6=timeout
            if status == 3:
                return result
            elif status in [4, 5, 6]:
                raise Exception(f"Task failed: {result.get('reason', 'Unknown error')}")
            
            time.sleep(poll_interval)
            elapsed += poll_interval
        
        raise TimeoutError(f"Task did not complete within {timeout} seconds")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python tianmu_text2video_client.py <app_key> <app_secret> <prompt> [resolution] [aspect_ratio]")
        sys.exit(1)
    
    app_key = sys.argv[1]
    app_secret = sys.argv[2]
    prompt = sys.argv[3]
    resolution = sys.argv[4] if len(sys.argv) > 4 else "720p"
    aspect_ratio = sys.argv[5] if len(sys.argv) > 5 else "16:9"
    
    client = TomovieeText2VideoClient(app_key, app_secret)
    
    try:
        print(f"Creating text-to-video task...")
        task_id = client.text_to_video(prompt, resolution, aspect_ratio=aspect_ratio)
        print(f"Task created: {task_id}")
        print("Polling for result...")
        
        result = client.poll_until_complete(task_id)
        
        print(f"\n✅ Task completed!")
        print(f"Progress: {result['progress']}%")
        
        result_data = json.loads(result['result'])
        print(f"Result: {json.dumps(result_data, indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
