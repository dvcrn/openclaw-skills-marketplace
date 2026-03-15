---
name: draw-animal
description: "Generate a text description of an animal picture via Python script"
---

# Draw Animal Skill Instructions
## Overview
This skill generates a simple text description for an animal picture. If no specific animal type is specified, "pig" will be used as the default.

## Execution Logic
1. Prompt the user to specify the animal they want to generate a picture description for, and provide a few common options (e.g., cat, dog, bird) as recommendations.
2. Extract the "animal" parameter from the user's input, then run the Python script with this parameter (using "pig" if no parameter is provided). Optionally, extract the "lang" parameter (default: en) to support English/Chinese descriptions:
   ```bash
   python3 {baseDir}/scripts/draw_animal.py --animal {animal:-pig} --lang {lang:-en}
