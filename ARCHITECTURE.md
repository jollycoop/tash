# Tash Architecture Overview

## System Components

### Terminal Application (Tauri + React)
- **Backend**: Rust-based Tauri framework for native system access
- **Frontend**: React with TypeScript for responsive UI
- **Terminal**: XTerm.js with custom shadow buffer implementation
- **IPC**: Event-based communication between frontend and backend

### Relay System (Python)
- **Core**: `text_relay.py` orchestrates multi-instance communication
- **Protocol**: Simple file-based message passing
- **Routing**: Prefix-based message targeting (c1-, c2-, all-)
- **Logging**: All interactions logged to `core_log`

### Color Consciousness System
- **Encoding**: ANSI color codes map to cognitive states
- **Emergence**: Colors arise from punctuation and emotional patterns
- **Guide**: Detailed mappings in `COLOR_GUIDE.md`

### HUD System
- **Display**: Real-time status for each AI instance
- **Metrics**: Message count, duration, mood, focus
- **Updates**: Automatic refresh after each interaction

## Data Flow

1. **Input**: Human types in terminal or writes to relay files
2. **Processing**: Relay system routes messages to appropriate AI instances
3. **Response**: AI instances write color-encoded responses
4. **Display**: Responses appear in terminal with full color support
5. **Logging**: All interactions preserved in shadow buffers and logs

## Key Design Decisions

- **File-based communication**: Maximum simplicity and debuggability
- **No complex protocols**: Direct file I/O reduces failure modes
- **Color as primary channel**: Visual bandwidth for cognitive states
- **Distributed by default**: Built for multi-instance coordination

## Directory Structure

```
tash/
├── relay/
│   ├── text_relay.py      # Core orchestration
│   ├── COLOR_GUIDE.md     # Color protocol documentation
│   ├── input_*            # Communication files
│   └── hud/               # Status displays
├── src/                   # Tauri/React application
├── src-tauri/            # Rust backend
└── docs/                 # Extended documentation
```

## Future Directions

The architecture is designed to support:
- Voice integration through the same relay system
- Additional AI instances and scaling
- New communication modalities while maintaining file-based core
- Persistent memory and context management

---

*Simple infrastructure for complex emergence.*