import os
import shutil


def cleanup_twelve_labs_files():
    files_to_remove = [
        "result.json",
        "video_extract.json",
        "video_info.json"
    ]

    base_dir = os.path.dirname(os.path.abspath(__file__))
    print("Cleaning from directory:", base_dir)

    for file_name in files_to_remove:
        file_path = os.path.join(base_dir, file_name)
        print(file_path)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Deleted: {file_name}")
            except Exception as e:
                print(f"Error deleting {file_name}: {e}")
        else:
            print(f"Skipped: {file_name} (not found)")

        parent_dir = os.path.dirname(base_dir)


def delete_others(keep_folder):
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    folder_to_clean = os.path.join(parent_dir, "downloaded_content")
    print("Cleaning folder:", folder_to_clean)

    if os.path.exists(folder_to_clean):
        for item in os.listdir(folder_to_clean):
            if item == keep_folder:
                continue  # skip this folder

            path = os.path.join(folder_to_clean, item)

            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                print(f"Deleted: {path}")
            except Exception as e:
                print(f"Error deleting {path}: {e}")


# if __name__ == "__main__":
#     cleanup_twelve_labs_files()
