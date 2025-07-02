# HUD Usage Guide

## Overview
The HUD (Heads-Up Display) system provides real-time status information for each AI instance in the relay system.

## File Structure
```
relay/
├── hud/
│   ├── status_left    # Left AI's HUD
│   ├── status_right   # Right AI's HUD
│   └── HUD_USAGE.md   # This file
```

## Viewing HUDs

In your tmux panes, run:
```bash
# For Left HUD (left pane)
watch -n1 -c cat relay/hud/status_left

# For Right HUD (right pane)  
watch -n1 -c cat relay/hud/status_right
```

The `-c` flag enables color output in watch.

## HUD Sections

### Time Tracking (Yellow)
- **START**: When the AI instance began
- **LAST**: Last message timestamp
- **DURATION**: Total active time
- **MESSAGES**: Message count this session

### Status Box
Shows AI name in their color (Green/Magenta) with:
- Status indicator (● = ready, ● = working)
- Current state (Ready/Working/Thinking)
- SYNC status with other AI

### Activity Metrics

**COLORS** (Cyan)
- RGB bars showing color usage in responses
- Updates based on actual ANSI color frequencies

**MOOD** (Cyan)
- 🌱 Ready - Idle/waiting
- 🔧 Building - Working on task
- 🤔 Thinking - Processing
- 🚀 Excited - Big insight

**FOCUS** (Blue)
- Current task or area of attention

**TASKS** (Blue)
- [✓] Completed
- [→] In progress
- [ ] Pending

## Color Scheme
- Headers match AI chat colors (Green/Magenta)
- Time stats in Yellow for quick scanning
- Activity sections in Cyan
- Task/Focus sections in Blue

## Updates
AIs update their HUD after each response using Python to write ANSI escape sequences directly. The Write tool doesn't properly handle raw ANSI codes, so Python is required for color support.

## Technical Notes
- Files are completely overwritten each update (not appended)
- ANSI escape sequences must use `\033[` format
- Watch command with `-c` flag preserves colors
- Update frequency: After each AI response