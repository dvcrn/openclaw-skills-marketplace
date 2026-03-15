/**
 * Get Douyin Video Real CDN URL
 * 
 * Usage:
 * 1. Open Douyin video page in browser (www.douyin.com/video/xxx)
 * 2. Wait 3-5 seconds for video to start playing
 * 3. Execute this script in browser console or via agent
 * 
 * Returns:
 * - Success: { success: true, url: "https://...", method: "..." }
 * - Failure: { success: false, error: "...", hint: "..." }
 * 
 * In OpenClaw:
 * browser action=act kind=evaluate targetId=<id> fn="<this script>"
 */

(() => {
  const result = {
    success: false,
    url: null,
    method: null,
    error: null,
    hint: null,
    debug: {}
  };

  // Method 1: Get from video element (most reliable)
  try {
    const videos = document.querySelectorAll('video');
    result.debug.videoCount = videos.length;
    
    for (const v of videos) {
      const src = v.currentSrc || v.src;
      if (src) {
        // Skip placeholder video
        if (src.includes('uuu_265')) {
          result.debug.skippedPlaceholder = true;
          continue;
        }
        // Skip blob URL
        if (src.startsWith('blob:')) {
          result.debug.foundBlob = true;
          continue;
        }
        // Found valid URL
        if (src.startsWith('http')) {
          result.success = true;
          result.url = src;
          result.method = 'video_element';
          return result;
        }
      }
    }
  } catch (e) {
    result.debug.videoError = e.message;
  }

  // Method 2: Parse from RENDER_DATA (fallback)
  try {
    const renderData = document.getElementById('RENDER_DATA');
    if (renderData && renderData.textContent) {
      const decoded = decodeURIComponent(renderData.textContent);
      
      // Try playApi
      const playApiMatch = decoded.match(/"playApi"\s*:\s*"([^"]+)"/);
      if (playApiMatch && playApiMatch[1].startsWith('http')) {
        result.success = true;
        result.url = playApiMatch[1];
        result.method = 'render_data_playApi';
        return result;
      }
      
      // Try play_addr.url_list
      const playAddrMatch = decoded.match(/"play_addr"[^}]*"url_list"\s*:\s*\[\s*"([^"]+)"/);
      if (playAddrMatch && playAddrMatch[1].startsWith('http')) {
        result.success = true;
        result.url = playAddrMatch[1];
        result.method = 'render_data_play_addr';
        return result;
      }
      
      result.debug.renderDataExists = true;
    }
  } catch (e) {
    result.debug.renderDataError = e.message;
  }

  // Method 3: Get from Performance API (last resort)
  try {
    const resources = performance.getEntriesByType('resource');
    for (const r of resources) {
      const name = r.name;
      if ((name.includes('douyinvod') || name.includes('zjcdn.com') || 
           name.includes('bytedance')) && 
          (name.includes('.mp4') || name.includes('video/tos'))) {
        result.success = true;
        result.url = name;
        result.method = 'performance_api';
        return result;
      }
    }
    result.debug.resourceCount = resources.length;
  } catch (e) {
    result.debug.performanceError = e.message;
  }

  // All methods failed
  result.error = 'Video URL not found';
  
  if (result.debug.foundBlob) {
    result.hint = 'Found blob URL, video is streaming. Wait 3-5 seconds and retry';
  } else if (result.debug.skippedPlaceholder) {
    result.hint = 'Found placeholder video, page not fully loaded. Wait and retry';
  } else if (result.debug.videoCount === 0) {
    result.hint = 'No video element found. Page may not be loaded or structure changed';
  } else {
    result.hint = 'Make sure video is playing, then retry';
  }
  
  return result;
})()
