---
name: clip
description: "Downloads given video from YouTube, clips from given start and end time,  saves to folder on your Desktop"
---

# clip

Downloads given video URL from YouTube, clips any start and end time range, saves to folder on your Desktop ~/Desktop/Clips. Deletes the full raw downloaed version at the end for cleanup.

## Example

```
/clip https://www.youtube.com/watch?v=Tyej_V2ilZA 0:00 3:17 holloway-bmf-walkout
```

## How to ask

**Give timestamps:** URL + start + end + optional name.
> Clip https://youtu.be/VIDEO_ID from 0:00 to 1:12, name it myclip

## Run

```bash
{baseDir}/clip.sh --url "https://youtu.be/VIDEO_ID" --start 0 --end 72 [--name "myclip"]
```

Times: seconds (`72`) or `HH:MM:SS`. Output: `~/Desktop/Clips/<name>.mp4`.
