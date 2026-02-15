"""
Extract video metadata and analyze thumbnail
Input: video_info.txt + summary JSON + thumbnail image
Output: video_extract.json
"""

import json
import os
from PIL import Image
from dotenv import load_dotenv

# For AI vision description
try:
    from transformers import pipeline
    USE_TRANSFORMERS = True
    print("✅ AI vision available (transformers installed)")
except ImportError:
    USE_TRANSFORMERS = False
    print("⚠️  AI vision not available. Install with: pip install transformers torch")

load_dotenv()

def analyze_thumbnail_with_ai(image_path):
    """
    Analyze thumbnail using BLIP model directly
    """
    if not USE_TRANSFORMERS:
        return "[AI vision not available]"
    
    try:
        print("🤖 Analyzing thumbnail with BLIP AI...")
        
        from transformers import BlipProcessor, BlipForConditionalGeneration
        import torch
        from PIL import Image
        
        # Load model
        processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        
        # Process image
        raw_image = Image.open(image_path).convert('RGB')
        
        # Conditional image captioning
        text = "a photography of"
        inputs = processor(raw_image, text, return_tensors="pt")
        
        out = model.generate(**inputs, max_new_tokens=50)
        description = processor.decode(out[0], skip_special_tokens=True)
        
        print(f"   ✅ Description: {description}")
        return description
        
    except Exception as e:
        print(f"⚠️  Error: {e}")
        return f"[Error analyzing thumbnail: {str(e)}]"

def extract_data():
    """
    Extract video metadata from summary JSON and analyze thumbnail
    Creates video_extract.json with all data
    """
    
    # ========== LOAD VIDEO INFO ==========
    if not os.path.exists('video_info.json'):
        print("❌ Error: video_info.txt not found!")
        print("Please run upload.py first.")
        exit(1)
    
    with open('video_info.json', 'r') as f:
        video_info = json.load(f)
    
    video_file = video_info.get('video_file', '')
    video_dir = os.path.dirname(video_file)
    video_name = os.path.splitext(os.path.basename(video_file))[0]
    
    # Construct file paths
    SUMMARY_FILE_PATH = os.path.join(video_dir, f"{video_name}_summary.json")
    THUMBNAIL_FILE_PATH = os.path.join(video_dir, f"{video_name}.webp")
    
    print(f"\n📁 Input files:")
    print(f"   Summary: {SUMMARY_FILE_PATH}")
    print(f"   Thumbnail: {THUMBNAIL_FILE_PATH}")
    
    # ========== EXTRACT FROM SUMMARY JSON ==========
    print("\n=== Reading Video Summary ===")
    
    video_title = ""
    video_description = ""
    tags = []
    
    if os.path.exists(SUMMARY_FILE_PATH):
        try:
            with open(SUMMARY_FILE_PATH, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                video_title = data.get("title", "")
                video_description = data.get("description", "")
                tags = data.get("tags", [])
                
                print(f"✅ Title: {video_title}")
                print(f"✅ Description: {video_description[:100]}...")
                print(f"✅ Tags: {len(tags)} tags found")
                
        except Exception as e:
            print(f"❌ Failed to read summary JSON: {e}")
            video_title = "[Error reading summary]"
            video_description = "[Error reading summary]"
            tags = []
    else:
        print(f"❌ Summary file not found: {SUMMARY_FILE_PATH}")
        video_title = "[Summary file not found]"
        video_description = "[Summary file not found]"
        tags = []
    
    # ========== ANALYZE THUMBNAIL ==========
    print("\n=== Analyzing Thumbnail ===")
    
    thumbnail_data_in_text_form = ""
    
    if os.path.exists(THUMBNAIL_FILE_PATH):
        # Use AI to analyze thumbnail
        thumbnail_data_in_text_form = analyze_thumbnail_with_ai(THUMBNAIL_FILE_PATH)
        print(f"✅ Thumbnail analyzed")
    else:
        print(f"❌ Thumbnail file not found: {THUMBNAIL_FILE_PATH}")
        thumbnail_data_in_text_form = "[Thumbnail file not found]"
    
    # ========== CREATE OUTPUT JSON ==========
    print("\n=== Creating video_extract.json ===")
    
    output_data = {
        "video_title": video_title,
        "video_description": video_description,
        "tags": tags,
        "thumbnail_data_in_text_form": thumbnail_data_in_text_form
    }
    
    output_file = "video_extract.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Output saved to: {output_file}")
    
    # Display output
    print("\n" + "="*60)
    print("EXTRACTED DATA")
    print("="*60)
    print(json.dumps(output_data, indent=2, ensure_ascii=False))
    print("="*60)
    
    return output_data

if __name__ == "__main__":
    extract_data()