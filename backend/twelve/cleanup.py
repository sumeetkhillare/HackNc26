import os

def cleanup_twelve_labs_files():
    """
    Removes temporary JSON files generated during the Twelve Labs pipeline.
    """
    # List of files to be removed from the current script directory
    files_to_remove = [
        "result.json",
        "video_extract.json",
        "video_info.json"
    ]

    print("Starting cleanup of Twelve Labs temporary files...")

    for file_name in files_to_remove:
        # Construct the path relative to the script's location
        file_path = os.path.join(os.getcwd(), file_name)
        
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"   Deleted: {file_name}")
            except Exception as e:
                print(f"   Error deleting {file_name}: {e}")
        else:
            print(f"   Skipped: {file_name} (File does not exist)")

    print(" Cleanup complete.")

if __name__ == "__main__":
    cleanup_twelve_labs_files()