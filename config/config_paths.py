import sys
import os



def get_base_dir():
    """Determine the base directory of the application.

    If the script is running as a bundled executable, return the executable's directory.
    Otherwise, return the project's base directory.
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


# Define base directory path
BASE_DIR = get_base_dir()

# Define paths for important files
CONFIG_PATH = os.path.join(BASE_DIR, "config", "settings.json")
STYLE_PATH = os.path.join(BASE_DIR, "resources", "style.qss")
ENV_PATH = os.path.join(BASE_DIR, ".env")
