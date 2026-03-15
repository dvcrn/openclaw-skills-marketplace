# Sprite Sheet Skill Package

Comprehensive guide to sprite sheets and texture atlases for efficient game asset management.

## 📁 Contents

```
sprite-sheet/
├── SKILL.md                  # Main documentation (concepts, frameworks, best practices)
├── TOOLS_COMPARISON.md       # Tool reviews, workflows, automation
├── README.md                 # This file
├── references/
│   ├── macroquad-guide.md   # Rust Macroquad sprite sheet API
│   ├── bevy-guide.md        # Rust Bevy TextureAtlas system
│   └── godot-guide.md       # Godot 4.x AnimatedSprite2D & AtlasTexture
└── examples/
    ├── rust-macroquad/
    │   ├── main.rs          # Full animation demo
    │   └── Cargo.toml       # WASM-ready config
    ├── rust-bevy/
    │   ├── main.rs          # ECS-based sprite animation
    │   └── Cargo.toml       # Bevy 0.15+ setup
    └── godot/
        ├── sprite_demo.gd   # GDScript implementation
        └── project.godot    # Godot 4.3 config
```

## 🚀 Quick Start

### 1. Understand the Concept
Read **SKILL.md** sections:
- Core Concepts (sprite sheet vs atlas)
- Framework implementations (Rust/Godot)
- Best practices

### 2. Choose Your Stack
- **Web Games (WASM)**: → Rust Macroquad (`references/macroquad-guide.md`)
- **Complex Games (ECS)**: → Rust Bevy (`references/bevy-guide.md`)
- **Visual Editor**: → Godot 4.x (`references/godot-guide.md`)

### 3. Pick a Tool
See **TOOLS_COMPARISON.md** for:
- TexturePacker (professional)
- Aseprite (pixel art creation)
- Kenney Asset Studio (for Kenney.nl assets)
- Free Texture Packer (web-based)

### 4. Run Examples
```bash
# Macroquad
cd examples/rust-macroquad
cargo run

# Bevy
cd examples/rust-bevy
cargo run

# Godot
# Open examples/godot/ in Godot 4.x editor
```

## 📚 Learning Path

### Beginner
1. Read SKILL.md "Core Concepts"
2. Try Free Texture Packer (web, no install)
3. Run examples/rust-macroquad (simplest code)

### Intermediate
1. Install Aseprite or TexturePacker
2. Create custom sprite sheet from PNGs
3. Implement animation system in your project
4. Study examples/rust-bevy for ECS patterns

### Advanced
1. Automate packing in CI/CD (see TOOLS_COMPARISON.md)
2. Implement texture atlas hot-reload
3. Optimize for mobile (compression, mipmaps)
4. Create custom atlas format for your engine

## 🎯 Use Cases Covered

✅ Loading sprite sheets from PNG + JSON  
✅ Frame-based animation (idle, run, jump)  
✅ Texture atlas metadata parsing  
✅ Pixel art filtering (nearest neighbor)  
✅ WASM deployment (web games)  
✅ Mobile optimization (size limits, compression)  
✅ Tool automation (CLI workflows)  
✅ Godot editor integration  

## 🔗 Related Skills

- **game-dev-rust-godot/** - Main tech stack guide
- **AGENTS.md** - Asset license policy (Kenney.nl CC0 for public games)

## 📝 License

Documentation: MIT  
Code examples: MIT (see individual files)  
Assets: Use Kenney.nl CC0 for public projects (see AGENTS.md)

## 🤝 Contributing

This is a personal knowledge base. If using externally:
1. Replace asset paths with your own
2. Test on target platforms (web, mobile)
3. Respect Kenney.nl CC0 license for public games

---

**Last Updated**: 2026-02-06  
**Version**: 1.0  
**Maintained By**: kjaylee workspace
