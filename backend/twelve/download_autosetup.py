import json
import os

def auto_setup_from_local():
    """
    Automatically detects the Video ID from the sibling 'downloaded_content' 
    folder and generates necessary Twelve Labs config files.
    """
    # 1. Navigation: Go back 1 folder to 'backend', then into 'downloaded_content'
    # Current location: backend/twelve
    twelve_dir = os.getcwd()
    backend_dir = os.path.dirname(twelve_dir)
    download_root = os.path.join(backend_dir, "downloaded_content")

    # 2. Automatically get the Video ID (the first subdirectory found)
    try:
        subfolders = [f.name for f in os.scandir(download_root) if f.is_dir()]
        if not subfolders:
            print(f" Error: No video folders found in {download_root}")
            return
        
        # Picking the first one found
        video_id = subfolders[0]
        print(f" Automatically detected Video ID: {video_id}")
    except FileNotFoundError:
        print(f" Error: Could not find directory {download_root}")
        return

    # 3. Construct paths to the existing files
    video_folder = os.path.join(download_root, video_id)
    video_file = os.path.join(video_folder, f"{video_id}.mp4")
    summary_file = os.path.join(video_folder, f"{video_id}_summary.json")

    # 4. Create video_info.json (Points upload.py to the existing MP4)
    if os.path.exists(video_file):
        video_info = {"video_file": os.path.abspath(video_file)}
        with open('video_info.json', 'w', encoding='utf-8') as f:
            json.dump(video_info, f, indent=2)
        print(f" Created video_info.json -> {video_id}.mp4")
    else:
        print(f" Warning: MP4 file not found at {video_file}")

    # # 5. Create video_extract.json (Mails existing metadata to analyze.py)
    # if os.path.exists(summary_file):
    #     with open(summary_file, 'r', encoding='utf-8') as f:
    #         meta = json.load(f)

    #     video_extract = {
    #         "video_title": meta.get("title", "Unknown Title"),
    #         "video_description": meta.get("description", ""),
    #         "tags": meta.get("tags", []),
    #         "thumbnail_data_in_text_form": f"Local video data for {video_id}"
    #     }

    #     with open('video_extract.json', 'w', encoding='utf-8') as f:
    #         json.dump(video_extract, f, indent=2, ensure_ascii=False)
    #     print(f" Created video_extract.json from {video_id}_summary.json")
    # else:
    #     print(f" Warning: Summary file not found at {summary_file}")

if __name__ == "__main__":
    auto_setup_from_local()