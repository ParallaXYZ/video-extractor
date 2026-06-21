#!/usr/bin/env python3
"""
Automatic download of required binaries for Video Extractor by ParallaXYZ

Downloads:
- yt-dlp.exe (latest release from GitHub)
- ffmpeg.exe (latest release from GitHub)
- node.exe (latest LTS from official Node.js)

Usage:
    python download_binaries.py
"""

import os
import sys
import urllib.request
import json
import zipfile
import shutil
from pathlib import Path


BIN_DIR = "bin"
TEMP_DIR = "temp_downloads"


def print_header(message):
    """Print section header"""
    print(f"\n{'='*70}")
    print(f"  {message}")
    print(f"{'='*70}\n")


def print_step(message):
    """Print step message"""
    print(f"→ {message}")


def download_file(url, destination, description="File"):
    """Download file with progress indication"""
    try:
        print_step(f"Downloading {description}...")
        print(f"  URL: {url}")
        print(f"  Destination: {destination}")
        
        # Create parent directory if needed
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        
        # Download with progress
        def reporthook(block_num, block_size, total_size):
            if total_size > 0:
                percent = min(block_num * block_size * 100 / total_size, 100)
                downloaded_mb = block_num * block_size / (1024 * 1024)
                total_mb = total_size / (1024 * 1024)
                print(f"\r  Progress: {percent:.1f}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)", end='')
        
        urllib.request.urlretrieve(url, destination, reporthook)
        print()  # New line after progress
        
        file_size_mb = os.path.getsize(destination) / (1024 * 1024)
        print(f"  ✓ Downloaded: {file_size_mb:.1f} MB")
        return True
        
    except Exception as e:
        print(f"\n  ✗ Error downloading {description}: {e}")
        return False


def get_latest_github_release(repo, asset_pattern):
    """Get latest release download URL from GitHub"""
    try:
        api_url = f"https://api.github.com/repos/{repo}/releases/latest"
        print_step(f"Fetching latest release info from {repo}...")
        
        req = urllib.request.Request(api_url)
        req.add_header('User-Agent', 'VideoExtractorByParallaXYZ')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            
        version = data.get('tag_name', 'unknown')
        print(f"  Latest version: {version}")
        
        # Find matching asset
        for asset in data.get('assets', []):
            if asset_pattern in asset['name'].lower():
                url = asset['browser_download_url']
                name = asset['name']
                print(f"  Found asset: {name}")
                return url, version
        
        print(f"  ✗ No asset matching '{asset_pattern}' found")
        return None, None
        
    except Exception as e:
        print(f"  ✗ Error fetching release info: {e}")
        return None, None


def download_ytdlp():
    """Download latest yt-dlp.exe"""
    print_header("Downloading yt-dlp")
    
    url, version = get_latest_github_release("yt-dlp/yt-dlp", "yt-dlp.exe")
    if not url:
        print("✗ Failed to get yt-dlp download URL")
        return False
    
    destination = os.path.join(BIN_DIR, "yt-dlp.exe")
    success = download_file(url, destination, f"yt-dlp {version}")
    
    if success:
        print(f"\n✓ yt-dlp {version} downloaded successfully")
    return success


def download_ffmpeg():
    """Download latest ffmpeg.exe"""
    print_header("Downloading FFmpeg")
    
    # FFmpeg releases are on GitHub (gyan.dev builds)
    # Using essentials build (smaller, has everything we need)
    url, version = get_latest_github_release("GyanD/codexffmpeg", "ffmpeg-release-essentials.zip")
    
    if not url:
        print("✗ Failed to get FFmpeg download URL")
        return False
    
    # Download zip
    os.makedirs(TEMP_DIR, exist_ok=True)
    zip_path = os.path.join(TEMP_DIR, "ffmpeg.zip")
    
    if not download_file(url, zip_path, f"FFmpeg {version}"):
        return False
    
    # Extract ffmpeg.exe
    try:
        print_step("Extracting ffmpeg.exe...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Find ffmpeg.exe in the archive
            ffmpeg_file = None
            for name in zip_ref.namelist():
                if name.endswith('bin/ffmpeg.exe'):
                    ffmpeg_file = name
                    break
            
            if not ffmpeg_file:
                print("  ✗ ffmpeg.exe not found in archive")
                return False
            
            # Extract to temp
            zip_ref.extract(ffmpeg_file, TEMP_DIR)
            
            # Move to bin directory
            os.makedirs(BIN_DIR, exist_ok=True)
            src = os.path.join(TEMP_DIR, ffmpeg_file)
            dst = os.path.join(BIN_DIR, "ffmpeg.exe")
            shutil.move(src, dst)
            
            file_size_mb = os.path.getsize(dst) / (1024 * 1024)
            print(f"  ✓ Extracted: {file_size_mb:.1f} MB")
        
        print(f"\n✓ FFmpeg {version} downloaded successfully")
        return True
        
    except Exception as e:
        print(f"  ✗ Error extracting FFmpeg: {e}")
        return False


def download_nodejs():
    """Download latest Node.js LTS"""
    print_header("Downloading Node.js")
    
    # Node.js LTS version (v20.x as of 2026)
    # Direct download from official site
    try:
        print_step("Fetching Node.js LTS info...")
        
        # Get latest LTS version info
        api_url = "https://nodejs.org/dist/index.json"
        req = urllib.request.Request(api_url)
        req.add_header('User-Agent', 'VideoExtractorByParallaXYZ')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            versions = json.loads(response.read().decode())
        
        # Find latest LTS
        lts_version = None
        for v in versions:
            if v.get('lts'):
                lts_version = v['version']
                lts_name = v.get('lts')
                print(f"  Latest LTS: {lts_version} ({lts_name})")
                break
        
        if not lts_version:
            print("  ✗ No LTS version found")
            return False
        
        # Download win-x64 zip
        url = f"https://nodejs.org/dist/{lts_version}/node-{lts_version}-win-x64.zip"
        
        os.makedirs(TEMP_DIR, exist_ok=True)
        zip_path = os.path.join(TEMP_DIR, "node.zip")
        
        if not download_file(url, zip_path, f"Node.js {lts_version}"):
            return False
        
        # Extract node.exe
        print_step("Extracting node.exe...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Find node.exe
            node_file = None
            for name in zip_ref.namelist():
                if name.endswith('node.exe'):
                    node_file = name
                    break
            
            if not node_file:
                print("  ✗ node.exe not found in archive")
                return False
            
            # Extract to temp
            zip_ref.extract(node_file, TEMP_DIR)
            
            # Move to bin directory
            os.makedirs(BIN_DIR, exist_ok=True)
            src = os.path.join(TEMP_DIR, node_file)
            dst = os.path.join(BIN_DIR, "node.exe")
            shutil.move(src, dst)
            
            file_size_mb = os.path.getsize(dst) / (1024 * 1024)
            print(f"  ✓ Extracted: {file_size_mb:.1f} MB")
        
        print(f"\n✓ Node.js {lts_version} downloaded successfully")
        return True
        
    except Exception as e:
        print(f"  ✗ Error downloading Node.js: {e}")
        return False


def cleanup_temp():
    """Clean up temporary download directory"""
    if os.path.exists(TEMP_DIR):
        try:
            shutil.rmtree(TEMP_DIR)
            print(f"\n✓ Cleaned up temporary files")
        except Exception as e:
            print(f"\n⚠ Warning: Could not clean up temp directory: {e}")


def check_existing_binaries():
    """Check which binaries already exist"""
    print_header("Checking existing binaries")
    
    binaries = {
        "yt-dlp.exe": os.path.join(BIN_DIR, "yt-dlp.exe"),
        "ffmpeg.exe": os.path.join(BIN_DIR, "ffmpeg.exe"),
        "node.exe": os.path.join(BIN_DIR, "node.exe"),
    }
    
    missing = []
    all_present = True
    
    for name, path in binaries.items():
        if os.path.exists(path):
            size_mb = os.path.getsize(path) / (1024 * 1024)
            print(f"  ✓ Found: {name} ({size_mb:.1f} MB)")
        else:
            print(f"  ✗ Missing: {name}")
            missing.append(name)
            all_present = False
    
    return all_present, missing


def main():
    """Main download workflow"""
    print("\n" + "="*70)
    print("  Video Extractor by ParallaXYZ - Binary Downloader")
    print("="*70)
    print("\nChecking required binaries:")
    print("  • yt-dlp.exe  - YouTube video downloader")
    print("  • ffmpeg.exe  - Video/audio processing")
    print("  • node.exe    - JavaScript runtime")
    print()
    
    # Check existing binaries
    all_present, missing = check_existing_binaries()
    
    if all_present:
        print("\n✓ All binaries are present. Nothing to download.")
        return 0
    
    # Automatically download missing binaries
    print(f"\nMissing binaries detected: {', '.join(missing)}")
    print("Attempting automatic download...\n")
    
    # Download missing files
    results = {}
    
    if "yt-dlp.exe" in missing:
        results["yt-dlp"] = download_ytdlp()
    
    if "ffmpeg.exe" in missing:
        results["ffmpeg"] = download_ffmpeg()
    
    if "node.exe" in missing:
        results["node"] = download_nodejs()
    
    # Cleanup
    cleanup_temp()
    
    # Summary
    print_header("Download Summary")
    
    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    for name, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {name}")
    
    print(f"\nCompleted: {success_count}/{total_count} successful")
    
    if success_count == total_count:
        print("\n✓ All required binaries downloaded successfully!")
        print("Continuing with build process...")
        return 0
    else:
        print("\n" + "="*70)
        print("  ✗ ERROR: Failed to download some binaries")
        print("="*70)
        print("\nSome binaries could not be downloaded automatically.")
        print("Please download them manually and place in the bin/ folder.\n")
        print("MANUAL DOWNLOAD INSTRUCTIONS:")
        print("-" * 70)
        
        if not results.get("yt-dlp", True):
            print("\n📥 yt-dlp.exe:")
            print("  1. Go to: https://github.com/yt-dlp/yt-dlp/releases/latest")
            print("  2. Download: yt-dlp.exe")
            print(f"  3. Place in: {os.path.abspath(BIN_DIR)}\\yt-dlp.exe")
        
        if not results.get("ffmpeg", True):
            print("\n📥 ffmpeg.exe:")
            print("  1. Go to: https://github.com/GyanD/codexffmpeg/releases/latest")
            print("  2. Download: ffmpeg-release-essentials.zip")
            print("  3. Extract ffmpeg.exe from bin/ folder")
            print(f"  4. Place in: {os.path.abspath(BIN_DIR)}\\ffmpeg.exe")
        
        if not results.get("node", True):
            print("\n📥 node.exe:")
            print("  1. Go to: https://nodejs.org/en/download/")
            print("  2. Download: Windows Binary (.zip) - 64-bit")
            print("  3. Extract node.exe")
            print(f"  4. Place in: {os.path.abspath(BIN_DIR)}\\node.exe")
        
        print("\n" + "-" * 70)
        print("\nAfter downloading, run build.bat again.")
        print("="*70)
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n✗ Download cancelled by user")
        cleanup_temp()
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        cleanup_temp()
        sys.exit(1)
