import os
def check_video_exists(video_url, download_folder="downloaded_content"):
    """
    Checks if a video has already been processed by looking for its 
    metadata summary file.
    """
    # Extract the video ID from the URL (simple version)
    if "v=" in video_url:
        video_id = video_url.split("v=")[1].split("&")[0]
    elif "be/" in video_url:
        video_id = video_url.split("be/")[1].split("?")[0]
    else:
        video_id = video_url # Fallback if ID is passed directly
        
    # Define the expected path to the metadata file
    # This matches your extractor's naming: folder/VIDEO_ID/VIDEO_ID_summary.json
    marker_file = os.path.join(download_folder, video_id, f"{video_id}_summary.json")
    
    return os.path.exists(marker_file), video_id