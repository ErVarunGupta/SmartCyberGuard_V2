import os
import tempfile

# =========================
# TARGET DIRECTORIES
# =========================
TARGET_DIRS = [
    tempfile.gettempdir(),              # temp
    os.path.expanduser("~\\Downloads")  # downloads
]


# =========================
# SCAN FILES
# =========================
def scan_files():
    junk_files = []
    total_size = 0

    for folder in TARGET_DIRS:
        if not os.path.exists(folder):
            continue

        for root, dirs, files in os.walk(folder):
            for file in files:
                try:
                    path = os.path.join(root, file)

                    # filter extensions
                    if file.endswith((".tmp", ".log", ".cache")):
                        size = os.path.getsize(path)

                        junk_files.append({
                            "path": path,
                            "size": size
                        })

                        total_size += size

                except:
                    continue

    return junk_files, total_size


# =========================
# DELETE FILES
# =========================
def delete_files(file_paths):
    deleted = 0

    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
                deleted += 1
        except:
            continue

    return deleted