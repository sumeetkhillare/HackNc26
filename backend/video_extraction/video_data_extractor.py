import yt_dlp
import os

def download_youtube_data(video_url):
    # Create a specific folder for downloads
    output_path = "downloaded_content"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    print(f"Starting download for: {video_url}")

    # Configure options for yt-dlp
    ydl_opts = {
        # --- Requirements 1 & 2: Paths and Metadata ---
        # Save files as 'Title/Title.extension' inside the download folder
        'outtmpl': f'{output_path}/%(title)s/%(title)s.%(ext)s',
        'writeinfojson': True,  # Saves Title, Description, Tags, Metadata to a .json file
        
        # --- Requirement 2: Download Video ---
        # Get best video and best audio, then merge them
        'format': 'bestvideo+bestaudio/best',
        
        # --- Requirement 3: Get Audio Only ---
        # Extract audio and convert to MP3
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'keepvideo': True, # Keep the video file after extracting audio
        
        # --- Requirement 4: Get Thumbnail ---
        'writethumbnail': True,
        
        # --- Requirement 5: Get Manual Subtitles ---
        'writesubtitles': True,
        'subtitleslangs': ['en'], # Focus on English
        
        # --- Requirement 8: Get Auto-Captions (Audio-to-Text) ---
        # Downloads YouTube's auto-generated captions if manual ones don't exist
        'writeautomaticsub': True,
        
        # --- Requirement 6: Get Comments ---
        'getcomments': True, 
        # Limit comments to 20 to avoid freezing on popular videos
        'extractor_args': {'youtube': {'max_comments': ['20','all','all','all']}},
        
        # --- Requirement 7: Get Chapters ---
        # Chapters are automatically included in the .json metadata file
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # This step downloads everything (Video, Audio, Subs, Thumbnails)
            info = ydl.extract_info(video_url, download=True)

            # Accessing data programmatically to print to console
            print("\n" + "="*30)
            print("EXTRACTION COMPLETE")
            print("="*30)
            print(f"1. Title: {info.get('title')}")
            print(f"2. Description Length: {len(info.get('description', ''))} chars")
            print(f"3. Tags: {info.get('tags')}")
            
            # Handling Chapters (Requirement 7)
            chapters = info.get('chapters')
            if chapters:
                print(f"7. Chapters Found: {len(chapters)}")
                for chapter in chapters:
                    print(f"   - {chapter['title']} ({chapter['start_time']}s)")
            else:
                print("7. No chapters found.")

            print(f"\nAll files saved in: {output_path}/{info.get('title')}/")

    except Exception as e:
        print(f"An error occurred: {e}")

# --- Entry Point ---
if __name__ == "__main__":
    # You can change this URL to test different videos
    video_link = "http://youtube.com/watch?v=mqXovE-n9EA&t=362s"
    download_youtube_data(video_link)