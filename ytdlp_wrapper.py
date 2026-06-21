# ytdlp_wrapper.py
"""Wrapper for calling yt-dlp.exe as external process"""

import os
import sys
import subprocess
import json
import re
from utils import ytdlp_path, ffmpeg_dir, node_path


def run_ytdlp(args, capture_output=True, timeout=None):
    """
    Run yt-dlp.exe with given arguments
    
    Args:
        args: List of command-line arguments
        capture_output: Whether to capture stdout/stderr
        timeout: Timeout in seconds
    
    Returns:
        subprocess.CompletedProcess object
    """
    ytdlp_exe = ytdlp_path()
    
    if not os.path.exists(ytdlp_exe):
        raise FileNotFoundError(f"yt-dlp.exe not found at: {ytdlp_exe}")
    
    cmd = [ytdlp_exe] + args
    
    creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
    
    return subprocess.run(
        cmd,
        capture_output=capture_output,
        text=True,
        timeout=timeout,
        creationflags=creationflags
    )


def extract_info(url, profile_path, download=False):
    """
    Extract video information using yt-dlp.exe
    
    Args:
        url: Video URL
        profile_path: Path to Edge profile directory
        download: Whether to download (False = info only)
    
    Returns:
        Dictionary with video information
    """
    ytdlp_exe = ytdlp_path()
    
    if not os.path.exists(ytdlp_exe):
        raise FileNotFoundError(f"yt-dlp.exe not found at: {ytdlp_exe}")
    
    # Build command
    cmd = [ytdlp_exe]
    
    # Add cookie extraction from Edge
    default_profile_path = os.path.join(profile_path, 'Default')
    cmd.extend(['--cookies-from-browser', f'edge:{default_profile_path}'])
    
    # Add node.js path for JavaScript challenges
    local_node = node_path()
    if os.path.exists(local_node):
        cmd.extend(['--exec-cmd', f'node:{local_node}'])
    
    # Add ffmpeg location
    ffmpeg_location = ffmpeg_dir()
    if os.path.exists(ffmpeg_location):
        cmd.extend(['--ffmpeg-location', ffmpeg_location])
    
    # Output as JSON
    cmd.extend(['--dump-json', '--no-playlist'])
    
    # Add URL
    cmd.append(url)
    
    # Run command
    creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        creationflags=creationflags
    )
    
    if result.returncode != 0:
        raise Exception(f"yt-dlp failed: {result.stderr}")
    
    # Parse JSON output
    try:
        info = json.loads(result.stdout)
        return info
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse yt-dlp output: {e}")


def download_video(url, profile_path, output_template, format_spec, progress_callback=None):
    """
    Download video using yt-dlp.exe
    
    Args:
        url: Video URL
        profile_path: Path to Edge profile directory
        output_template: Output filename template
        format_spec: Format specification string
        progress_callback: Function to call with progress updates
    
    Returns:
        True if successful
    """
    ytdlp_exe = ytdlp_path()
    
    if not os.path.exists(ytdlp_exe):
        raise FileNotFoundError(f"yt-dlp.exe not found at: {ytdlp_exe}")
    
    # Build command
    cmd = [ytdlp_exe]
    
    # Add cookie extraction from Edge
    default_profile_path = os.path.join(profile_path, 'Default')
    cmd.extend(['--cookies-from-browser', f'edge:{default_profile_path}'])
    
    # Add node.js path for JavaScript challenges
    local_node = node_path()
    if os.path.exists(local_node):
        cmd.extend(['--exec-cmd', f'node:{local_node}'])
    
    # Add ffmpeg location
    ffmpeg_location = ffmpeg_dir()
    if os.path.exists(ffmpeg_location):
        cmd.extend(['--ffmpeg-location', ffmpeg_location])
    
    # Format and output
    cmd.extend(['-f', format_spec])
    cmd.extend(['-o', output_template])
    
    # No playlist
    cmd.append('--no-playlist')
    
    # Progress output
    cmd.append('--newline')
    
    # Add URL
    cmd.append(url)
    
    # Run command with live output
    creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        creationflags=creationflags,
        bufsize=1,
        universal_newlines=True
    )
    
    # Read output line by line
    for line in process.stdout:
        line = line.strip()
        if line and progress_callback:
            # Parse progress from output
            # Example: [download]  45.2% of 123.45MiB at 1.23MiB/s ETA 00:30
            match = re.search(r'\[download\]\s+([\d.]+)%', line)
            if match:
                percent = float(match.group(1))
                progress_callback(percent, line)
            elif '[download]' in line or 'Merging' in line or 'Deleting' in line:
                progress_callback(None, line)
    
    process.wait()
    
    if process.returncode != 0:
        raise Exception(f"yt-dlp download failed with code {process.returncode}")
    
    return True


def download_audio(url, profile_path, output_template, progress_callback=None):
    """
    Download and extract audio using yt-dlp.exe
    
    Args:
        url: Video URL
        profile_path: Path to Edge profile directory
        output_template: Output filename template
        progress_callback: Function to call with progress updates
    
    Returns:
        True if successful
    """
    ytdlp_exe = ytdlp_path()
    
    if not os.path.exists(ytdlp_exe):
        raise FileNotFoundError(f"yt-dlp.exe not found at: {ytdlp_exe}")
    
    # Build command
    cmd = [ytdlp_exe]
    
    # Add cookie extraction from Edge
    default_profile_path = os.path.join(profile_path, 'Default')
    cmd.extend(['--cookies-from-browser', f'edge:{default_profile_path}'])
    
    # Add node.js path for JavaScript challenges
    local_node = node_path()
    if os.path.exists(local_node):
        cmd.extend(['--exec-cmd', f'node:{local_node}'])
    
    # Add ffmpeg location
    ffmpeg_location = ffmpeg_dir()
    if os.path.exists(ffmpeg_location):
        cmd.extend(['--ffmpeg-location', ffmpeg_location])
    
    # Extract audio
    cmd.extend(['-x', '--audio-format', 'm4a', '--audio-quality', '192K'])
    
    # Format: best audio
    cmd.extend(['-f', 'bestaudio[ext=m4a]/bestaudio'])
    
    # Output template
    cmd.extend(['-o', output_template])
    
    # No playlist
    cmd.append('--no-playlist')
    
    # Progress output
    cmd.append('--newline')
    
    # Add URL
    cmd.append(url)
    
    # Run command with live output
    creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        creationflags=creationflags,
        bufsize=1,
        universal_newlines=True
    )
    
    # Read output line by line
    for line in process.stdout:
        line = line.strip()
        if line and progress_callback:
            # Parse progress from output
            match = re.search(r'\[download\]\s+([\d.]+)%', line)
            if match:
                percent = float(match.group(1))
                progress_callback(percent, line)
            elif '[download]' in line or 'Extracting' in line or 'Deleting' in line or 'Post-processing' in line:
                progress_callback(None, line)
    
    process.wait()
    
    if process.returncode != 0:
        raise Exception(f"yt-dlp audio extraction failed with code {process.returncode}")
    
    return True
