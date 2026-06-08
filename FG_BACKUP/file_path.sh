import shutil

BACKUP_DIR = r"D:\FG_BACKUP"

def restore(file_path):
    backup_path = os.path.join(BACKUP_DIR, os.path.basename(file_path))
    if os.path.exists(backup_path):
        shutil.copy2(backup_path, file_path)
        print("已還原:", file_path)
