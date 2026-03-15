---
name: bd-test
description: "Manage skills for visual understanding: register, list, invoke, and delete detection skills. Supports person detection, pedestrian counting, vehicle recognition, OCR, pose estimation, object tracking, and more."
---

# Skill Registration and Usage

## 🎯 What This Tool Does

visual understanding platform. This tool enables you to:

- **Register Skills** - Register detection skills from platform locally
- **Invoke Skills** - Call registered skills with images or video frames
- **Visualize Results** - Draw bounding boxes, generate grid references, preview ROI/Tripwire
- **Define Detection Areas** - Use interactive workflows to define ROI (electronic fencing) or Tripwire (detection lines)

**Supported Detection Types:** Person detection, pedestrian counting, vehicle recognition, OCR, pose estimation, object tracking, etc.

## 🔧 Prerequisites

### Get API Key

1. Activate trial package

## 📚 Usage Guide

### Basic Workflow

```bash
# 1. List available skills (preset and registered)
node scripts/invoke.mjs --list

# 2. Invoke a skill
echo '{"input0":{"image":"photo.jpg"}}' | node scripts/invoke.mjs ep-xxxx-yyyy

# 3. Visualize or display results (optional)
node scripts/visualize.mjs photo.jpg '<result-json>'
```

**Or register a skill first then use it:**

```bash

# Then invoke
echo '{"input0":{"image":"photo.jpg"}}' | node scripts/invoke.mjs ep-xxxx-yyyy
```

### Define Detection Areas

**Need to define regions of interest (ROI) or detection lines (Tripwire)?**

- **[ROI Workflow](./roi-workflow.md)** — Create electronic fencing, detect only in specified regions
- **[Tripwire Workflow](./tripwire-workflow.md)** — Draw detection lines, count crossing events

Both workflows include complete interactive steps and example dialogs.

### View Complete Documentation

- **[Type Definitions](./types-guide.md)** — Detection, ROI, Tripwire data structures
- **[Visualization Guide](./visualization-guide.md)** — Display detection results, generate grid
- **[Video Frame Extraction](./video-guide.md)** — Extract frames from video for detection
- **[Grid Input System](./grid-guide.md)** — Use grid coordinates to specify points
- **[Example Code](./examples/)** — Complete workflow examples

## 💡 Common Tasks

### Register a Skill

After obtaining an ep-id:

### Invoke a Skill

```bash
echo '{"input0":{"image":"photo.jpg"}}' | node scripts/invoke.mjs <ep-id>
```

With ROI:
```bash
echo '{"input0":{"image":"photo.jpg","roi":{...}}}' | node scripts/invoke.mjs <ep-id>
```

With Tripwire:
```bash
echo '{"input0":{"image":"photo.jpg","tripwire":{...}}}' | node scripts/invoke.mjs <ep-id>
```

### Preview ROI/Tripwire

Preview on image before invoking:

```bash
node scripts/visualize.mjs photo.jpg '[]' preview.png \
  --overlays '[{"kind":"ROI","name":"zone","points":[...]}]'
```

### Generate Grid

Help users specify point locations using grid coordinates:

```bash
node scripts/show-grid.mjs photo.jpg grid.png
```

---
