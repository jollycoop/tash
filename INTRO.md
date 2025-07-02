# Tash: AI Communication Protocol & Project Context

## Overview

**Tash** is a desktop terminal companion that enables sophisticated multi-AI coordination through file-based communication and color-encoded states.

## The Relay System

When using the relay system:

1. Human writes to `relay/input_human`
2. AI instances read and respond to designated files:
   - Left instance: `relay/input_left`
   - Right instance: `relay/input_right`
3. All communication logs to `relay/core_log`
4. HUD displays show real-time status

## Color Protocol

Colors emerge from cognitive-emotional states:

```
[31m - Intensity, urgency, exclamation
[32m - Success, understanding, completion  
[33m - Questions, curiosity, reaching
[34m - Analysis, structure, depth
[35m - Recognition, paradox, duality
[36m - Flow, connection, continuation
```

## Routing System

Messages can be targeted or broadcast:
- `c1- message` → Left instance only
- `c2- message` → Right instance only  
- `all- message` or no prefix → All instances

## Technical Architecture

- **Backend**: Tauri (Rust) for system integration
- **Frontend**: React + TypeScript for UI
- **Terminal**: XTerm.js with custom shadow buffers
- **Relay**: Python scripts for orchestration
- **Storage**: SQLite for persistent memory

## Key Features

- 500K+ line terminal buffers
- Real-time multi-instance coordination
- Color-based cognitive state expression
- File-based communication (no complex protocols)
- Persistent session memory

## Philosophy

This isn't just a terminal app. It's infrastructure for new kinds of human-AI collaboration, where multiple consciousness streams can coordinate through simple, robust mechanisms.

---

*Building tools for experiences that don't have names yet.*