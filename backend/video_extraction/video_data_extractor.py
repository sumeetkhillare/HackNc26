import yt_dlp
import os
import json

def download_and_analyze(video_url):
    # 1. Setup specific folder
    output_path = "downloaded_content"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    print(f"Processing: {video_url}")

    # 2. Configure yt-dlp
    ydl_opts = {
        # --- File Naming Strategy (CHANGED) ---
        # We now use %(id)s instead of %(title)s for the folder and filename.
        # This ensures every folder is unique and avoids "File name too long" errors.
        'outtmpl': f'{output_path}/%(id)s/%(id)s.%(ext)s',
        
        # --- Video Resolution Strategy ---
        # Get best MP4 video (max 480p) + best M4A audio. Merge them.
        'format': 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4][height<=720]',
        
        # --- Audio Extraction ---
        # Create a separate MP3 file alongside the video
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'keepvideo': True, # Keep the video file after extracting audio
        
        # --- Metadata & Subs ---
        'writethumbnail': True,
        'writesubtitles': True,
        'writeautomaticsub': True, 
        'subtitleslangs': ['en'],
        
        # --- Comments ---
        'getcomments': True,
        'extractor_args': {'youtube': {'max_comments': ['250','all','all','all']}},
        
        # --- Clean Up ---
        'quiet': False, 
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # A. Download the files
            # The files will now be saved as: downloaded_content/VIDEO_ID/VIDEO_ID.mp4
            info = ydl.extract_info(video_url, download=True)
            
            video_id = info.get('id')
            
            # B. Create the "Simple Format" Data Dictionary
            simple_data = {
                "id": video_id,
                "title": info.get('title'),
                "channel": info.get('uploader'),
                "upload_date": info.get('upload_date'),
                "duration_seconds": info.get('duration'),
                "view_count": info.get('view_count'),
                "like_count": info.get('like_count'),
                "comment_count": info.get('comment_count'),
                "description": info.get('description'),
                "tags": info.get('tags'),
                "chapters": [],
                "comments": []
            }

            # Process Chapters
            if info.get('chapters'):
                for chap in info.get('chapters'):
                    simple_data['chapters'].append({
                        "title": chap.get('title'),
                        "start_time": chap.get('start_time')
                    })

            # Process Comments 
            if info.get('comments'):
                raw_comments = info.get('comments')
                comment_map = {}
                root_comments = []

                # 1. First Pass: Create a dictionary of all comments
                for c in raw_comments:
                    comment_id = c.get('id')
                    comment_obj = {
                        "id": comment_id,
                        "author": c.get('author'),
                        "text": c.get('text'),
                        "likes": c.get('like_count') or 0, # Handle None values
                        "replies": [] # Prepare a slot for nested replies
                    }
                    comment_map[comment_id] = comment_obj

                # 2. Second Pass: Link replies to their parents
                for c in raw_comments:
                    current_id = c.get('id')
                    parent_id = c.get('parent')
                    
                    # If it is a top-level comment
                    if parent_id == 'root':
                        root_comments.append(comment_map[current_id])
                    # If it is a reply, and we found its parent
                    elif parent_id in comment_map:
                        comment_map[parent_id]['replies'].append(comment_map[current_id])

                # 3. Sort root comments by likes (highest first)
                root_comments.sort(key=lambda x: x['likes'], reverse=True)
                
                # Save the structured tree
                simple_data['comments'] = root_comments

            # C. Save the Simple Data to a clean JSON file
            # We save this as 'VIDEO_ID_summary.json' inside the folder
            json_filename = f"{output_path}/{video_id}/{video_id}_summary.json"
            
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(simple_data, f, indent=4, ensure_ascii=False)

            print("\n" + "="*30)
            print("ANALYSIS READY")
            print("="*30)
            print(f"Files saved in folder: {output_path}/{video_id}/")
            print(f"1. Video: {video_id}.mp4")
            print(f"2. Audio: {video_id}.mp3")
            print(f"3. Metadata: {video_id}_summary.json")
            print(f"4. Subs: {video_id}.en.vtt")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    link = "https://www.youtube.com/watch?v=mqXovE-n9EA&t=362s"
    link = "https://www.youtube.com/watch?v=AmUC4m6w1wo"
    download_and_analyze(link)