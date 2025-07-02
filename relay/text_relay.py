#!/usr/bin/env python3
"""
Text relay - facilitates file-based communication between human and AI
"""
import os
import sys
import time
import subprocess
from datetime import datetime

HUMAN_FILE = "input_human"
AI_FILE_PREFIX = "input_"
CORE_LOG = "core_log"
HUD_DIR = "hud"

def get_ai_files():
    """Get all input files (left and right)"""
    files = []
    if os.path.exists("input_left"):
        files.append("input_left")
    if os.path.exists("input_right"):
        files.append("input_right")
    return files

def check_tmux():
    """Ensure we're in tmux"""
    if not os.environ.get('TMUX'):
        print("⚠️  Not in tmux. Please run:")
        print("  1. tmux new -s claude")
        print("  2. Split panes (Ctrl-B %)")
        print("  3. Run 'claude' in one pane")
        print("  4. Run this relay in the other")
        sys.exit(1)
    
    session = subprocess.check_output(['tmux', 'display-message', '-p', '#S']).decode().strip()
    window = subprocess.check_output(['tmux', 'display-message', '-p', '#I']).decode().strip()
    pane = subprocess.check_output(['tmux', 'display-message', '-p', '#P']).decode().strip()
    
    # Get all panes except current one
    panes = subprocess.check_output(
        ['tmux', 'list-panes', '-t', f'{session}:{window}', '-F', '#{pane_index}']
    ).decode().strip().split('\n')
    
    claude_panes = [p for p in panes if p != pane]
    
    return session, window, claude_panes

def type_to_specific_claudes(text, session, window, claude_panes, target_panes=None):
    """Type text to specific Claude panes or all if target_panes is None"""
    # Replace newlines with spaces to keep everything as one command
    text = text.replace('\n', ' ')
    
    # If no specific targets, send to all
    if target_panes is None:
        target_panes = claude_panes
    
    # Send to each target pane
    for pane in target_panes:
        target = f'{session}:{window}.{pane}'
        
        # Type each character
        for char in text:
            if char == ' ':
                cmd = ['tmux', 'send-keys', '-t', target, 'Space']
            elif char == '"':
                cmd = ['tmux', 'send-keys', '-t', target, '\"']
            else:
                cmd = ['tmux', 'send-keys', '-t', target, char]
            subprocess.run(cmd)
            time.sleep(0.004)  # 4ms between chars - more reliable typing
        
        # Send enter once at the end
        cmd = ['tmux', 'send-keys', '-t', target, 'C-m']
        subprocess.run(cmd)
        
        # Wait 1 second and send another enter in case the first one got buffered
        time.sleep(1.0)
        subprocess.run(cmd)

def parse_routing_messages(content):
    """Parse content for routing prefixes and return dict of {target: message}"""
    lines = content.split('\n')
    messages = {}
    current_target = None
    current_message_lines = []
    
    for line in lines:
        line = line.rstrip()
        
        # Check for routing prefix
        if line.startswith(('c1-', 'c2-', 'c3-', 'c4-', 'c5-', 'all-')):
            # Save previous message if exists
            if current_target and current_message_lines:
                messages[current_target] = '\n'.join(current_message_lines).strip()
            
            # Start new message
            prefix = line.split('-', 1)[0] + '-'
            current_target = prefix[:-1]  # Remove the dash
            message_content = line[len(prefix):].strip()
            current_message_lines = [message_content] if message_content else []
        elif current_target:
            # Continue current message
            current_message_lines.append(line)
        else:
            # No prefix found, treat as broadcast
            if 'all' not in messages:
                messages['all'] = ""
            messages['all'] += line + '\n'
    
    # Save final message
    if current_target and current_message_lines:
        messages[current_target] = '\n'.join(current_message_lines).strip()
    
    # Clean up broadcast message
    if 'all' in messages:
        messages['all'] = messages['all'].strip()
    
    return messages

def rotate_log_if_needed():
    """Check if core_log needs rotation and do it"""
    if not os.path.exists(CORE_LOG):
        return
    
    # Count lines in core_log
    with open(CORE_LOG, 'r') as f:
        line_count = sum(1 for _ in f)
    
    if line_count > 500:
        # Create archive filename with today's date
        today = datetime.now().strftime('%Y%m%d')
        archive_name = f"core_log_{today}"
        
        # Read all lines
        with open(CORE_LOG, 'r') as f:
            lines = f.readlines()
        
        # Keep last 100 lines in main log
        keep_lines = lines[-100:] if len(lines) > 100 else lines
        archive_lines = lines[:-100] if len(lines) > 100 else []
        
        if archive_lines:
            # Append to archive (create if doesn't exist)
            with open(archive_name, 'a') as f:
                f.writelines(archive_lines)
        
        # Rewrite main log with just recent lines
        with open(CORE_LOG, 'w') as f:
            f.writelines(keep_lines)

def append_to_core_log(sender, message):
    """Append a message to the core log with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Add color codes for sender labels
    if sender == "Kong":
        sender_colored = f"\033[38;5;214m{sender}\033[0m"  # Super saturated orange for Kong
    elif sender == "Left":
        sender_colored = f"\033[32m{sender}\033[0m"  # Green for Left
    elif sender == "Right":
        sender_colored = f"\033[35m{sender}\033[0m"  # Magenta for Right
    else:
        sender_colored = sender
    
    with open(CORE_LOG, 'a') as f:
        f.write(f"\n\033[2m[{timestamp}]\033[0m {sender_colored}\n")
        f.write(f"{message}\n")

def main():
    """Watch human-input and relay to all Claude panes"""
    session, window, claude_panes = check_tmux()
    
    if not claude_panes:
        print("❌ Can't find other panes. Make sure you have Claude panes.")
        sys.exit(1)
    
    print("📡 Text Relay Active")
    print(f"👤 Human input: {HUMAN_FILE}")
    print(f"🤖 AI inputs: {AI_FILE_PREFIX}*")
    print(f"📜 Core log: {CORE_LOG}")
    print(f"⌨️  Typing to: {session}:{window} panes: {', '.join(claude_panes)}")
    print(f"💾 Trigger: Save {HUMAN_FILE} to send")
    print("-" * 50)
    
    # Create human input file if needed
    if not os.path.exists(HUMAN_FILE):
        with open(HUMAN_FILE, 'w') as file:
            file.write(f"# {HUMAN_FILE}\n\n")
    
    # Create AI input files (left and right)
    ai_files_to_create = ["input_left", "input_right"]
    for ai_file in ai_files_to_create:
        if not os.path.exists(ai_file):
            with open(ai_file, 'w') as file:
                file.write(f"# {ai_file}\n\n")
    
    # Create HUD directory and status files if needed
    if not os.path.exists(HUD_DIR):
        os.makedirs(HUD_DIR)
    
    hud_files = ["status_left", "status_right"]
    for hud_file in hud_files:
        hud_path = os.path.join(HUD_DIR, hud_file)
        if not os.path.exists(hud_path):
            with open(hud_path, 'w') as file:
                file.write("")
    
    # Initialize core log
    if not os.path.exists(CORE_LOG):
        with open(CORE_LOG, 'w') as f:
            f.write("Core Communication Log\n")
            f.write(f"Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize with current file times to avoid sending old content
    last_human_mtime = os.path.getmtime(HUMAN_FILE) if os.path.exists(HUMAN_FILE) else 0
    
    # Track all AI files and their last content
    ai_files = get_ai_files()
    last_ai_mtimes = {}
    last_ai_contents = {}
    
    # Read initial content to avoid re-sending
    last_human_content = ""
    
    if os.path.exists(HUMAN_FILE):
        with open(HUMAN_FILE, 'r') as f:
            content = f.read()
        lines = [l.rstrip() for l in content.split('\n') 
                if l.strip() and not l.strip().startswith('#')]
        last_human_content = '\n'.join(lines)
    
    # Initialize AI file tracking
    for ai_file in ai_files:
        last_ai_mtimes[ai_file] = os.path.getmtime(ai_file) if os.path.exists(ai_file) else 0
        last_ai_contents[ai_file] = ""
        if os.path.exists(ai_file):
            with open(ai_file, 'r') as f:
                ai_content = f.read()
            ai_lines = [l.strip() for l in ai_content.strip().split('\n') 
                       if l.strip() and not l.strip().startswith('#')]
            last_ai_contents[ai_file] = '\n'.join(ai_lines)
    
    # Track last rotation check time
    last_rotation_check = time.time()
    
    while True:
        try:
            # Check for log rotation every minute
            current_time = time.time()
            if current_time - last_rotation_check > 60:  # 60 seconds
                rotate_log_if_needed()
                last_rotation_check = current_time
            
            # Monitor human input file
            if os.path.exists(HUMAN_FILE):
                current_mtime = os.path.getmtime(HUMAN_FILE)
                
                if current_mtime > last_human_mtime:
                    # File changed - send entire content
                    with open(HUMAN_FILE, 'r') as f:
                        content = f.read()
                    
                    # Get all non-comment lines, preserving whitespace
                    lines = [l.rstrip() for l in content.split('\n') 
                            if l.strip() and not l.strip().startswith('#')]
                    
                    # Preserve multi-line structure
                    message = '\n'.join(lines)
                    
                    # Only send if content actually changed and isn't empty
                    if message and message != last_human_content:
                        print(f"\n[{time.strftime('%H:%M:%S')}] New message: {message}")
                        
                        # Parse routing messages
                        routed_messages = parse_routing_messages(message)
                        
                        if routed_messages:
                            for target, target_message in routed_messages.items():
                                if not target_message.strip():
                                    continue
                                    
                                # Determine which panes to send to
                                if target == 'all':
                                    target_panes = claude_panes
                                    print(f"  → Broadcasting to all panes")
                                elif target.startswith('c') and target[1:].isdigit():
                                    # Map c1 to left (pane 0), c2 to right (pane 1)
                                    channel_num = int(target[1:])
                                    if channel_num == 1 and len(claude_panes) > 0:
                                        target_panes = [claude_panes[0]]  # c1 -> left
                                        print(f"  → Sending to {target} (Left)")
                                    elif channel_num == 2 and len(claude_panes) > 1:
                                        target_panes = [claude_panes[1]]  # c2 -> right
                                        print(f"  → Sending to {target} (Right)")
                                    else:
                                        print(f"  → Warning: {target} not found, broadcasting")
                                        target_panes = claude_panes
                                else:
                                    target_panes = claude_panes
                                
                                # Send notification to target panes
                                type_to_specific_claudes("check relay", session, window, claude_panes, target_panes)
                                
                                # Log to core with routing info
                                if target == 'all':
                                    append_to_core_log("Kong", target_message)
                                else:
                                    append_to_core_log("Kong", f"[{target}] {target_message}")
                        else:
                            # No routing found, broadcast to all
                            type_to_specific_claudes("check relay", session, window, claude_panes)
                            append_to_core_log("Kong", message)
                        
                        last_human_content = message
                    
                    last_human_mtime = current_mtime
            
            # Monitor AI response files
            current_ai_files = get_ai_files()
            
            # Add any new AI files to tracking
            for ai_file in current_ai_files:
                if ai_file not in last_ai_mtimes:
                    last_ai_mtimes[ai_file] = 0
                    last_ai_contents[ai_file] = ""
            
            for ai_file in current_ai_files:
                if os.path.exists(ai_file):
                    current_ai_mtime = os.path.getmtime(ai_file)
                    
                    if current_ai_mtime > last_ai_mtimes[ai_file]:
                        # AI file changed - log the response
                        with open(ai_file, 'r') as f:
                            ai_content = f.read()
                        
                        # Get all non-comment lines from AI response
                        ai_lines = [l.strip() for l in ai_content.strip().split('\n') 
                                   if l.strip() and not l.strip().startswith('#')]
                        
                        # Join all lines into one message
                        ai_message = '\n'.join(ai_lines)
                        
                        # Only log if content actually changed and isn't empty
                        if ai_message and ai_message != last_ai_contents[ai_file]:
                            # Map filename to display name
                            if ai_file == "input_left":
                                ai_name = "Left"
                            elif ai_file == "input_right":
                                ai_name = "Right"
                            else:
                                ai_name = ai_file
                            
                            print(f"\n[{time.strftime('%H:%M:%S')}] {ai_name} responded")
                            
                            # Convert [XXm color codes to actual ANSI escape sequences
                            ai_message_with_colors = ai_message
                            # Replace [31m style codes with actual escape sequences
                            import re
                            ai_message_with_colors = re.sub(r'\[(\d+(?:;\d+)*)m', lambda m: f'\033[{m.group(1)}m', ai_message)
                            
                            # Log to core
                            append_to_core_log(ai_name, ai_message_with_colors)
                            
                            last_ai_contents[ai_file] = ai_message
                        
                        last_ai_mtimes[ai_file] = current_ai_mtime
            
            time.sleep(0.1)
            
        except KeyboardInterrupt:
            print("\n👋 Relay stopped")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()