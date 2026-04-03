import os

# 🔥 OUTPUT FILE NAME
OUTPUT_FILE = "project_full_dump.txt"

# ❌ Ignore folders (important)
IGNORE_DIRS = {
    "venv", "__pycache__", ".git", "dist", "build",
    ".idea", ".vscode", "node_modules"
}

# ✅ Allowed file types
ALLOWED_EXT = {".py", ".txt", ".md", ".json", ".yaml", ".yml", ".spec"}


def write_structure(root, file):
    file.write("📁 PROJECT STRUCTURE\n")
    file.write("=" * 50 + "\n\n")

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

        level = dirpath.replace(root, "").count(os.sep)
        indent = " " * 4 * level
        file.write(f"{indent}{os.path.basename(dirpath)}/\n")

        subindent = " " * 4 * (level + 1)
        for f in filenames:
            file.write(f"{subindent}{f}\n")


def write_file_contents(root, file):
    file.write("\n\n📄 FILE CONTENTS\n")
    file.write("=" * 50 + "\n\n")

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

        for fname in filenames:
            ext = os.path.splitext(fname)[1]

            if ext not in ALLOWED_EXT:
                continue

            filepath = os.path.join(dirpath, fname)

            file.write(f"\n\n--- {filepath} ---\n\n")

            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    file.write(f.read())
            except Exception as e:
                file.write(f"⚠️ Could not read file: {e}\n")


def main():
    root_dir = os.getcwd()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        write_structure(root_dir, out)
        write_file_contents(root_dir, out)

    print(f"\n✅ Project exported successfully to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()