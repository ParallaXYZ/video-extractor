# utils.py
"""Common utilities and functions"""

import os
import sys
import re
import subprocess

# Constants
APP_NAME = "Video extractor by ParallaXYZ"
DEFAULT_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
EDGE_PROFILE_DIR = os.path.join(os.environ['LOCALAPPDATA'], 'Video Extractor by ParallaXYZ', 'edge_profile')


def get_app_dir():
    """Get application directory (where .exe is located or script directory)"""
    if getattr(sys, "frozen", False):
        # Running as compiled executable
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))


def get_bin_dir():
    """Get bin directory path"""
    return os.path.join(get_app_dir(), "bin")


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    # For icons and other resources bundled in _MEIPASS
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)


def ffmpeg_path():
    """Returns path to ffmpeg.exe"""
    return os.path.join(get_bin_dir(), "ffmpeg.exe")


def ffmpeg_dir():
    """Returns path to bin directory (contains ffmpeg.exe) - for backward compatibility"""
    return get_bin_dir()


def ytdlp_path():
    """Returns path to yt-dlp.exe"""
    return os.path.join(get_bin_dir(), "yt-dlp.exe")


def node_path():
    """Returns path to local node.exe"""
    node_exe = os.path.join(get_bin_dir(), "node.exe")
    
    # Check if file exists
    if os.path.exists(node_exe):
        return node_exe
    
    # Fallback to system node (if local not found)
    print(f"⚠️ Local node.exe not found at path: {node_exe}")
    print("⚠️ Using system node (if installed)")
    return "node"


def human_size(n):
    """Converts bytes to human-readable format"""
    if not n or n <= 0:
        return ""
    for u in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024:
            return f"{n:.1f} {u}"
        n /= 1024.0
    return f"{n:.1f} PB"


def classify(f):
    """Classifies format (video/audio/muxed)"""
    ac = f.get("acodec") or "none"
    vc = f.get("vcodec") or "none"
    if ac != "none" and vc != "none":
        return "muxed"
    if vc != "none":
        return "video"
    if ac != "none":
        return "audio"
    return "unknown"


def parse_percent(s: str):
    """Parses percentage from string"""
    m = re.search(r"([\d.]+)%", s)
    return float(m.group(1)) if m else None


def is_cookie_error(error_msg: str) -> bool:
    """Checks if error is related to cookies"""
    error_lower = error_msg.lower()
    keywords = [
        "winerror 32",
        "process cannot access",
        "cookie database",
        "permission denied",
        "failed to decrypt",
        "locked",
        "database is locked",
    ]
    has_keyword = any(kw in error_lower for kw in keywords)
    has_context = "cookie" in error_lower or "database" in error_lower or "edge" in error_lower
    return has_keyword and has_context


def check_edge_auth() -> bool:
    """Checks if user is authorized in Edge"""
    cookies_db = os.path.join(EDGE_PROFILE_DIR, "Default", "Network", "Cookies")
    
    if not os.path.exists(cookies_db):
        return False
    
    try:
        import sqlite3
        conn = sqlite3.connect(f"file:{cookies_db}?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM cookies WHERE host_key LIKE '%youtube.com%'")
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except:
        return False


def open_auth_edge():
    """Launches Microsoft Edge for authorization"""
    edge_path = os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe")
    executable = edge_path if os.path.exists(edge_path) else "msedge.exe"
    
    try:
        subprocess.Popen([
            executable,
            f'--user-data-dir={EDGE_PROFILE_DIR}',
            '--no-first-run',
            '--disable-autofill',
            'https://www.youtube.com'
        ])
    except Exception as e:
        print(f"Error launching Edge: {e}")


def ensure_edge_profile_dir():
    """Creates Edge profile folder if it doesn't exist"""
    os.makedirs(EDGE_PROFILE_DIR, exist_ok=True)
