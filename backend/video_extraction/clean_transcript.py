import re
import os

def clean_vtt(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    clean_lines = []
    
    # Pattern for timestamps (00:00:00.000 --> 00:00:00.000)
    timestamp_pattern = re.compile(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}')
    # Pattern for metadata tags (like <c> or <i>)
    tag_pattern = re.compile(r'<[^>]*>')

    for line in lines:
        line = line.strip()
        
        # Skip header, timestamps, and empty lines
        if not line or line == "WEBVTT" or line.startswith("Kind:") or line.startswith("Language:"):
            continue
        if timestamp_pattern.search(line):
            continue
            
        # Remove tags and add to list
        clean_text = tag_pattern.sub('', line)
        if clean_text:
            clean_lines.append(clean_text)

    # Join lines and remove consecutive duplicate phrases (common in YT auto-subs)
    final_text = []
    for line in clean_lines:
        if not final_text or line != final_text[-1]:
            final_text.append(line)

    return " ".join(final_text)

# --- Usage ---
if __name__ == "__main__":
    vtt_file = r"C:\Users\Admin\Desktop\Personal\mlh2026\HackNc26\backend\video_extraction\downloaded_content\mqXovE-n9EA\mqXovE-n9EA.en.vtt" # Change this to your file path
    text = clean_vtt(vtt_file)
    
    if text:
        print("\n--- Cleaned Transcript ---\n")
        print(text)
        
        # Optional: Save to a text file
        with open("transcript.txt", "w", encoding="utf-8") as out:
            out.write(text)