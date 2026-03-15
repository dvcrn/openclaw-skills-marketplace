---
name: voice-to-protocol-transcriber
description: "Record experimental procedures and observations via voice commands during"
---

# Voice-to-Protocol Transcriber

## Description

Record operation steps and observations via voice commands during experiments. Suitable for laboratory environments, helping researchers transcribe experimental operations in real-time and generate structured experiment records.

## Use Cases

- Chemistry experiment operation recording
- Biology experiment step tracking
- Physics experiment data recording
- Clinical experiment operation logging
- Any scenario requiring real-time step recording

## Dependencies

```bash
pip install speechrecognition pyaudio pydub python-docx
```

## Configuration

Configure in `~/.openclaw/config/voice-to-protocol-transcriber.json`:

```json
{
  "language": "zh-CN",
  "output_format": "markdown",
  "auto_save_interval": 60,
  "save_directory": "~/Documents/Experiment-Protocols",
  "experiment_name": "default",
  "enable_timestamp": true,
  "voice_commands": {
    "start_recording": "开始记录",
    "stop_recording": "停止记录",
    "add_observation": "观察到",
    "add_step": "步骤",
    "save_protocol": "保存记录",
    "add_note": "备注"
  }
}
```

## Usage

### Basic Usage

```bash
openclaw skill voice-to-protocol-transcriber --config config.json
```

### Quick Start

```bash
# Start voice recording
openclaw skill voice-to-protocol-transcriber --experiment "Cell Culture Experiment-2024-02-06"

# Use specific language
openclaw skill voice-to-protocol-transcriber --lang en-US
```

### Voice Commands

| Command | Description |
|------|------|
| "Start Recording" | Start voice recognition and recording |
| "Step [content]" | Add an experiment step |
| "Observed [content]" | Add observation results |
| "Note [content]" | Add additional notes |
| "Save Record" | Save current experiment record |
| "Stop Recording" | End recording and save |

## Output Format

### Markdown Format

```markdown
# Experiment Record: [Experiment Name]

**Date**: 2024-02-06  
**Time**: 14:30:25  
**Recorder**: [User]

---

## Step 1
**Time**: 14:31:00  
**Operation**: [Voice transcription content]

## Observation 1
**Time**: 14:32:15  
**Content**: [Observation result]

## Note 1
**Time**: 14:35:00  
**Content**: [Note information]

---

*Experiment record ended at 14:45:00*
```

## API

### Python Call

```python
from skills.voice_to_protocol_transcriber import ProtocolTranscriber

# Initialize
transcriber = ProtocolTranscriber(
    experiment_name="My Experiment",
    language="zh-CN"
)

# Start listening
transcriber.start_listening()

# Add manual entry
transcriber.add_step("Prepare petri dish")
transcriber.add_observation("Culture medium became turbid")

# Save and stop
transcriber.save()
transcriber.stop()
```

## Features

- 🎙️ Real-time voice recognition
- 📝 Automatic classification (Step/Observation/Note)
- ⏱️ Automatic timestamps
- 💾 Auto-save
- 🌐 Multi-language support
- 📄 Multiple output formats (Markdown/Word/Plain Text)
- 🔇 Voice command control

## Notes

- First use requires microphone permission
- Recommended to use in quiet environments
- Chinese recognition requires good network connection
- Save regularly to avoid data loss

## Changelog

### 1.0.0
- Initial version release
- Support Chinese and English voice recognition
- Markdown and Word output formats
- Voice command control

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python/R scripts executed locally | Medium |
| Network Access | No external API calls | Low |
| File System Access | Read input files, write output files | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Output files saved to workspace | Low |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] Input file paths validated (no ../ traversal)
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no stack traces exposed)
- [ ] Dependencies audited
## Prerequisites

```bash
# Python dependencies
pip install -r requirements.txt
```

## Evaluation Criteria

### Success Metrics
- [ ] Successfully executes main functionality
- [ ] Output meets quality standards
- [ ] Handles edge cases gracefully
- [ ] Performance is acceptable

### Test Cases
1. **Basic Functionality**: Standard input → Expected output
2. **Edge Case**: Invalid input → Graceful error handling
3. **Performance**: Large dataset → Acceptable processing time

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-06
- **Known Issues**: None
- **Planned Improvements**: 
  - Performance optimization
  - Additional feature support
