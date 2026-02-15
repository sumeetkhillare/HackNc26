from valkey_rest.crud import valkey_exists

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
        video_id = video_url  # Fallback if ID is passed directly

    return valkey_exists(video_id + "_summary.json"), video_id
