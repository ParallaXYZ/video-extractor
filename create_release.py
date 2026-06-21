#!/usr/bin/env python3
# create_release.py
"""
Automated release creation script for Video Extractor by ParallaXYZ

This script:
1. Builds the application using PyInstaller
2. Creates the release directory structure
3. Copies all necessary files (exe, binaries, icons)
4. Creates a ZIP archive ready for distribution

Usage:
    python create_release.py
"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path


# Configuration
APP_NAME = "Video Extractor By ParallaXYZ"
RELEASE_DIR_NAME = "Video extractor by ParallaXYZ"
SPEC_FILE = "VideoExtractorByParallaXYZ.spec"
BIN_DIR = "bin"
ICONS_DIR = "icons"


def print_step(message):
    """Print a step message"""
    print(f"\n{'='*60}")
    print(f"  {message}")
    print(f"{'='*60}\n")


def check_prerequisites():
    """Check if all required files exist"""
    print_step("Checking prerequisites")
    
    required_files = [
        SPEC_FILE,
        "app.py",
        "download_tab.py",
        "convert_tab.py",
        "utils.py",
        "ytdlp_wrapper.py",
        "translations.py",
        "requirements.txt",
    ]
    
    required_binaries = [
        os.path.join(BIN_DIR, "yt-dlp.exe"),
        os.path.join(BIN_DIR, "ffmpeg.exe"),
        os.path.join(BIN_DIR, "node.exe"),
    ]
    
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
            print(f"❌ Missing: {file}")
        else:
            print(f"✓ Found: {file}")
    
    for binary in required_binaries:
        if not os.path.exists(binary):
            missing_files.append(binary)
            print(f"❌ Missing: {binary}")
        else:
            print(f"✓ Found: {binary}")
    
    if missing_files:
        print(f"\n❌ Error: Missing {len(missing_files)} required file(s)")
        print("Please ensure all files are present before building.")
        return False
    
    print("\n✓ All prerequisites satisfied")
    return True


def verify_binaries():
    """Verify that binaries work"""
    print_step("Verifying binaries")
    
    binaries = {
        "yt-dlp.exe": ["--version"],
        "ffmpeg.exe": ["-version"],
        "node.exe": ["--version"],
    }
    
    all_ok = True
    
    for binary, args in binaries.items():
        binary_path = os.path.join(BIN_DIR, binary)
        try:
            result = subprocess.run(
                [binary_path] + args,
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                print(f"✓ {binary}: {version}")
            else:
                print(f"❌ {binary}: Failed to run")
                all_ok = False
        except Exception as e:
            print(f"❌ {binary}: Error - {e}")
            all_ok = False
    
    if not all_ok:
        print("\n❌ Some binaries failed verification")
        return False
    
    print("\n✓ All binaries verified")
    return True


def build_application():
    """Build the application using PyInstaller"""
    print_step("Building application with PyInstaller")
    
    try:
        # Run PyInstaller
        cmd = ["pyinstaller", "--clean", SPEC_FILE]
        print(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=False
        )
        
        # Check if exe was created
        exe_path = os.path.join("dist", f"{APP_NAME}.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\n✓ Build successful: {exe_path} ({size_mb:.1f} MB)")
            return True
        else:
            print(f"\n❌ Build failed: {exe_path} not found")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"\n❌ PyInstaller failed with error code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n❌ Build error: {e}")
        return False


def create_release_structure():
    """Create the release directory structure"""
    print_step("Creating release structure")
    
    # Paths
    release_root = "release"
    release_app_dir = os.path.join(release_root, RELEASE_DIR_NAME)
    release_bin_dir = os.path.join(release_app_dir, "bin")
    
    # Clean up old release
    if os.path.exists(release_root):
        print(f"Removing old release directory: {release_root}")
        shutil.rmtree(release_root)
    
    # Create directories
    os.makedirs(release_app_dir, exist_ok=True)
    os.makedirs(release_bin_dir, exist_ok=True)
    print(f"✓ Created: {release_app_dir}")
    print(f"✓ Created: {release_bin_dir}")
    
    # Copy executable
    exe_src = os.path.join("dist", f"{APP_NAME}.exe")
    exe_dst = os.path.join(release_app_dir, f"{APP_NAME}.exe")
    shutil.copy2(exe_src, exe_dst)
    print(f"✓ Copied: {APP_NAME}.exe")
    
    # Copy binaries
    binaries = ["yt-dlp.exe", "ffmpeg.exe", "node.exe"]
    for binary in binaries:
        src = os.path.join(BIN_DIR, binary)
        dst = os.path.join(release_bin_dir, binary)
        shutil.copy2(src, dst)
        print(f"✓ Copied: bin/{binary}")
    
    # Copy README if exists
    if os.path.exists("README.md"):
        shutil.copy2("README.md", os.path.join(release_app_dir, "README.md"))
        print(f"✓ Copied: README.md")
    
    # Copy LICENSE if exists
    if os.path.exists("LICENSE.md"):
        shutil.copy2("LICENSE.md", os.path.join(release_app_dir, "LICENSE.md"))
        print(f"✓ Copied: LICENSE.md")
    
    print(f"\n✓ Release structure created in: {release_app_dir}")
    return release_app_dir


def create_zip_archive(release_app_dir):
    """Create ZIP archive of the release"""
    print_step("Creating ZIP archive")
    
    release_root = "release"
    zip_name = f"{RELEASE_DIR_NAME}.zip"
    zip_path = os.path.join(release_root, zip_name)
    
    # Remove old zip if exists
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    # Create zip with root folder
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through the release directory
        for root, dirs, files in os.walk(release_app_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Calculate archive name (preserve folder structure)
                arcname = os.path.relpath(file_path, release_root)
                zipf.write(file_path, arcname)
                print(f"  Added: {arcname}")
    
    zip_size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"\n✓ ZIP archive created: {zip_path} ({zip_size_mb:.1f} MB)")
    return zip_path


def verify_release(release_app_dir):
    """Verify the release structure"""
    print_step("Verifying release")
    
    required_items = [
        f"{APP_NAME}.exe",
        "bin/yt-dlp.exe",
        "bin/ffmpeg.exe",
        "bin/node.exe",
    ]
    
    all_ok = True
    for item in required_items:
        item_path = os.path.join(release_app_dir, item)
        if os.path.exists(item_path):
            size_mb = os.path.getsize(item_path) / (1024 * 1024)
            print(f"✓ {item} ({size_mb:.1f} MB)")
        else:
            print(f"❌ Missing: {item}")
            all_ok = False
    
    if not all_ok:
        print("\n❌ Release verification failed")
        return False
    
    print("\n✓ Release verified successfully")
    return True


def main():
    """Main release creation workflow"""
    print("\n" + "="*60)
    print("  Video Extractor by ParallaXYZ - Release Builder")
    print("="*60)
    
    # Step 1: Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Step 2: Verify binaries
    if not verify_binaries():
        print("\n⚠️  Warning: Some binaries failed verification")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Step 3: Build application
    if not build_application():
        sys.exit(1)
    
    # Step 4: Create release structure
    release_app_dir = create_release_structure()
    if not release_app_dir:
        sys.exit(1)
    
    # Step 5: Verify release
    if not verify_release(release_app_dir):
        sys.exit(1)
    
    # Step 6: Create ZIP archive
    zip_path = create_zip_archive(release_app_dir)
    if not zip_path:
        sys.exit(1)
    
    # Success!
    print_step("Release creation complete!")
    print(f"✓ Release directory: {release_app_dir}")
    print(f"✓ ZIP archive: {zip_path}")
    print("\nYou can now distribute the ZIP file to users.")
    print("Users should extract the entire folder and run the .exe from there.")
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
