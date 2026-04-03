import os
import time

USER_PATH = os.path.expanduser("~")

FOLDERS_TO_SCAN = [
    os.path.join(USER_PATH, "Downloads"),
    os.path.join(USER_PATH, "Desktop"),
    os.path.join(USER_PATH, "AppData", "Local", "Temp")
]

def scan_files(folders):
    files_data = []

    for folder in folders:
        if not os.path.exists(folder):
            continue

        for root, dirs, files in os.walk(folder):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    
                    size = os.path.getsize(file_path)
                    modified_time = os.path.getmtime(file_path)

                    files_data.append({
                        "path": file_path,
                        "size": size,
                        "last_modified": modified_time
                    })

                except:
                    continue

    return files_data


def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024



def analyze_files(files):
    current_time = time.time()

    results = []

    for f in files:
        age_days = (current_time - f["last_modified"]) / (60 * 60 * 24)
        size_mb = f["size"] / (1024 * 1024)

        category = "Important"

        # Rule-based classification
        if "Temp" in f["path"]:
            category = "Safe"

        elif age_days > 30 and size_mb > 50:
            category = "Maybe"

        elif age_days > 60:
            category = "Safe"

        elif size_mb > 100:
            category = "Maybe"

        elif age_days < 7:
            category = "Important"

        results.append({
            "path": f["path"],
            "size": f["size"],
            "age_days": age_days,
            "category": category
        })

    return results


def delete_files(files):
    deleted = 0
    failed = 0

    for f in files:
        try:
            os.remove(f["path"])
            deleted += 1
        except:
            failed += 1

    return deleted, failed


def get_safe_files(analyzed_files):
    safe_files = [f for f in analyzed_files if f["category"] == "Safe"]

    total_size = sum(f["size"] for f in safe_files)

    return safe_files, total_size


if __name__ == "__main__":
    files = scan_files(FOLDERS_TO_SCAN)
    analyzed = analyze_files(files)

    safe_files, total_size = get_safe_files(analyzed)

    print(f"\n🟢 Safe files: {len(safe_files)}")
    print(f"💾 Total space to free: {format_size(total_size)}\n")

    # Show first few safe files
    for f in safe_files[:10]:
        print(f["path"])

    # Confirmation
    confirm = input("\nDo you want to delete these files? (yes/no): ")

    if confirm.lower() == "yes":
        deleted, failed = delete_files(safe_files)
        print(f"\n✅ Deleted: {deleted} files")
        print(f"❌ Failed: {failed} files")
    else:
        print("\n❌ Deletion cancelled")