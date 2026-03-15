# Seedance 2.0 Professional User Guide

## Core Specifications
- **Model Architecture**: Multimodal Video Generation (Text/Image/Video/Audio -> Video)
- **Default Duration**: **15 Seconds** (Standard for professional clips)
- **Supported Inputs**: Text, Image, Video, Audio

## The "Director's Toolkit" (Seedance 2.0 Capabilities)

### 1. Reference System (The Control Center)
Seedance 2.0 allows for precise control via reference inputs. This is crucial for professional workflows.
- **Reference Image (Composition & Detail)**: Use this to lock in:
    - **Composition**: Rule of thirds, center framing, golden ratio.
    - **Character Consistency**: Clothing, facial features.
    - **Art Style**: Oil painting, 3D render, film stock (e.g., Kodak Portra 400).
- **Reference Video (Motion & Rhythm)**: Use this to clone:
    - **Camera Language**: Dolly zooms, tracking shots, handheld shake.
    - **Motion Rhythm**: Slow motion, speed ramps, complex character acting.
- **Reference Audio (Atmosphere & Pacing)**:
    - **Rhythm Sync**: The video cuts and motion will align with the audio beats.
    - **Mood Setting**: Sad music generates slower, more melancholic visual pacing.

### 2. Camera Language (Cinematography)
- **Shot Size**: Extreme Long Shot (ELS), Long Shot (LS), Medium Shot (MS), Close-up (CU), Extreme Close-up (ECU).
- **Angles**: Eye-level, High Angle (vulnerability), Low Angle (power), Dutch Angle (disorientation), Bird's Eye, Worm's Eye.
- **Movement**:
    - **Static**: No movement.
    - **Pan**: Horizontal rotation.
    - **Tilt**: Vertical rotation.
    - **Dolly/Tracking**: Moving the camera toward/away/alongside the subject.
    - **Truck**: Moving the camera left/right.
    - **Crane/Boom**: Moving the camera up/down.
    - **Handheld**: Organic, shaky, realistic.
    - **FPV**: First-person view (dynamic drone shots).

### 3. Lighting & Atmosphere
- **Key**: High Key (bright, optimistic), Low Key (dark, dramatic, horror).
- **Direction**: Backlight (silhouettes, halo), Sidelight (texture, drama), Top light.
- **Quality**: Hard Light (sharp shadows), Soft Light (diffused, flattering).
- **Color Palette**:
    - **Teal & Orange**: Hollywood blockbuster look.
    - **Monochromatic**: Single color dominance.
    - **Neon/Cyberpunk**: High contrast, saturated colors.
    - **Pastel**: Soft, desaturated, dreamy.

### 4. Sound Design (Audio-Driven Generation)
- **Diegetic**: Sounds originating from the source (footsteps, dialogue, wind).
- **Non-Diegetic**: Score, voiceover, sound effects (SFX).
- **Atmosphere**: Ambient noise, room tone.

## Prompt Structure Recommendation

For professional results, organize the prompt hierarchically:

```
[Cinematography/Camera] + [Subject/Character] + [Action/Performance] + [Environment/Set] + [Lighting/Atmosphere] + [Technical Specs/Style]
```

**Example**:
> "Low angle, dolly in shot. A weary astronaut in a tattered white spacesuit walking slowly towards a glowing monolith. Martian landscape, red dust swirling. High contrast lighting, strong backlight from the monolith, deep shadows. Cinematic, IMAX quality, 8k resolution, highly detailed texture. --ar 16:9 --motion 5"
