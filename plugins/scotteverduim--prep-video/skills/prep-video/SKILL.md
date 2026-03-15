---
name: prep-video
description: "Prep Video"
---

# PREP-VIDEO SKILL

## Overview
This skill provides a command to prepare videos by checking and confirming the necessary assets are available before generating the video.

## COMMAND
- **/prep-video <script_id>**

## FUNCTIONALITY
1. Downloads the specified JSON script from Google Drive.
2. Parses the JSON for summary information including:
   - Script ID
   - Video title
   - Number of scenes and their types
   - Voiceover file path and existence status
   - A-roll clips needed and their existence status
3. Checks for the presence of all required assets on Google Drive.
4. If all assets are present, triggers the video generation script.
5. If assets are missing, notifies the user of missing files and their required locations.