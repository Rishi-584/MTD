
import sys

TARGET_FILE = 'mtd_controller.py'

def fix_file():
    with open(TARGET_FILE, 'r') as f:
        lines = f.readlines()

    new_lines = []
    
    # State flags
    in_garbage_block = False
    indenting_block = False
    
    # Markers
    MARKER_START = "pcap_result = {'found': False, 'output': '', 'error': None}"
    MARKER_GARBAGE_END = "except Exception:"
    MARKER_SESSION_ID = "session_id = str(uuid.uuid4())"
    MARKER_END_BLOCK = "except Exception as e:"
    
    # Indentation constants
    TARGET_INDENT = " " * 24 
    
    iterator = iter(lines)
    
    for line in iterator:
        stripped = line.strip()
        
        # 1. Detect Start
        if MARKER_START in line:
            new_lines.append(line)
            # Add the new try block immediately after pcap_result init
            # Line is "                    pcap_result = ..." (20 spaces)
            # We want try: at 20 spaces
            indent = line[:len(line) - len(line.lstrip())]
            new_lines.append(f"{indent}try:\n")
            in_garbage_block = True
            continue
            
        # 2. Skip Garbage Block
        if in_garbage_block:
            if MARKER_SESSION_ID in line:
                in_garbage_block = False
                indenting_block = True
                # Handle this first line of the block
                # We force it to TARGET_INDENT
                new_lines.append(TARGET_INDENT + stripped + "\n")
            else:
                continue
            continue
            
        # 3. Indent the main block
        if indenting_block:
            if MARKER_END_BLOCK in line:
                indenting_block = False
                new_lines.append(line) # The closing except block (at 20 spaces)
            else:
                if stripped == "":
                    new_lines.append(line)
                else:
                    # Smart re-indentation
                    # We want to ensure at least 24 spaces.
                    # If line has < 24 spaces, force 24.
                    # If line has >= 24 spaces, keep it (assuming it was already correct or relative)
                    # BUT wait, lines 375-400 are 20 spaces. They need to become 24.
                    # Lines 400+ are 24 spaces. They should stay 24?
                    # No, lines 400+ were originally inside the try block (at 24).
                    # But now I am wrapping them in a NEW try block?
                    # The original structure:
                    # try: (20)
                    #     code (24)
                    # except: (20)
                    #
                    # My structure:
                    # try: (20)
                    #     code (24)
                    # except: (20)
                    
                    # So proper indentation is 24 spaces for ALL lines inside.
                    
                    # If a line is currently 20 spaces, it needs +4.
                    # If a line is currently 24 spaces, it needs +0.
                    
                    current_indent_len = len(line) - len(line.lstrip())
                    
                    if current_indent_len == 20:
                         new_lines.append("    " + line)
                    elif current_indent_len >= 24:
                         new_lines.append(line)
                    else:
                         # Fallback for weirdly indented lines (like 0 or 4)
                         # Should not happen in this block, but just in case
                         new_lines.append(TARGET_INDENT + stripped + "\n")
                         
            continue
            
        # Default: keep line
        new_lines.append(line)

    with open(TARGET_FILE, 'w') as f:
        f.writelines(new_lines)
    
    print("File patched.")

if __name__ == "__main__":
    fix_file()
