import os
import shutil
from pathlib import Path


class CacheCleaner:
    @staticmethod
    def clean_python_cache():
        """
        Remove all __pycache__ directories and .pyc/.pyo files
        from the project root directory (App).
        """

        # Get absolute path of project root (App folder)
        BASE_DIR = Path(__file__).resolve().parent

        removed_dirs = 0
        removed_files = 0

        for root, dirs, files in os.walk(BASE_DIR):

            # Remove __pycache__ directories
            for dir_name in dirs:
                if dir_name == "__pycache__":
                    dir_path = Path(root) / dir_name
                    try:
                        shutil.rmtree(dir_path)
                        print(f"Removed directory: {dir_path}")
                        removed_dirs += 1
                    except Exception as e:
                        print(f"Failed to remove {dir_path}: {e}")

            # Remove .pyc and .pyo files
            for file_name in files:
                if file_name.endswith((".pyc", ".pyo")):
                    file_path = Path(root) / file_name
                    try:
                        file_path.unlink()
                        print(f"Removed file: {file_path}")
                        removed_files += 1
                    except Exception as e:
                        print(f"Failed to remove {file_path}: {e}")

        print("\nCleanup completed successfully.")
        print(f"Total __pycache__ directories removed: {removed_dirs}")
        print(f"Total compiled files removed: {removed_files}")


if __name__ == "__main__":
    CacheCleaner.clean_python_cache()
