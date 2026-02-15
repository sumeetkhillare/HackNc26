import os

from valkey_rest import crud

# Add this function to your utils.py


def check_analysis_exists(video_id, download_folder="downloaded_content"):
    """Checks if the AI comment analysis already exists."""
    analysis_file_key = f"{video_id}_analysis.json"
    analysis_file = os.path.join(download_folder, video_id, f"{video_id}_analysis.json") 
    return crud.valkey_exists(analysis_file_key), analysis_file
