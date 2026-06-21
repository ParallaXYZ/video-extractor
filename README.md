# Video extractor by ParallaXYZ

**Universal application for downloading videos from YouTube and converting video files**

## 🚀 Quick Start

### 📦 Download Ready-to-Use Application

**For regular users (no Python required):**

1. Go to [Releases](../../releases)
2. Download `Video Extractor By ParallaXYZ.exe.zip`
3. Extract the archive
4. Run `Video Extractor By ParallaXYZ.exe`

### 💻 Run from Source Code

**For developers:**

#### Requirements
- Windows 10/11
- Python 3.8+
- Microsoft Edge (for YouTube authorization)

#### Installation

1. Clone the repository:
```bash
git clone https://github.com/ParallaXYZ/video-extractor.git
cd video-extractor
```

2. Create virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

#### Build Executable

To build your own `.exe` file:

```bash
build.bat
```

The build script will automatically:
1. Install Python dependencies
2. Download required binaries (yt-dlp, ffmpeg, node.js)
3. Build the executable with PyInstaller
4. Create release package in `release/` folder

The executable will be created in `dist\Video Extractor By ParallaXYZ.exe.exe`

## 📖 Main Features

### 📥 Download from YouTube

1. **Authorization**
   - Click "Edge Authorization"
   - Sign in to your YouTube account
   - Close the browser after signing in

2. **Video Analysis**
   - Paste YouTube video link
   - Click "Analyze"
   - Select desired format from the table

3. **Download**
   - Select format in the table
   - Click "Download selected"
   - File will be saved to the selected folder

**Available formats:**
- Video: from 144p to 4K (including 50/60fps)
- Audio: various bitrates
- Combined: video+audio in one file

**Filters:**
- All formats
- Video only
- Audio only
- Combined

### 🔄 Video Conversion

1. **Select File**
   - Click "Select video file..."
   - Choose local video file

2. **Configure Settings**
   - **Video codec**: H.264, H.265 or no re-encoding
   - **Audio codec**: AAC, MP3 or no re-encoding
   - **Quality (CRF)**: 18-28 (lower is better)
   - **Audio bitrate**: 128k - 320k
   - **Container**: mp4, mkv, avi, webm

3. **Convert**
   - Click "🚀 Start Conversion"
   - Wait for the process to complete

**CRF Recommendations:**
- **18-20**: High quality, large file size
- **23**: Optimal balance (recommended)
- **26-28**: Low quality, small file size

## 🎯 Features

✅ **Isolated Authorization** - uses separate Edge profile, doesn't affect main browser

✅ **All YouTube Formats** - including Premium formats (720p50, 1080p50, 4K)

✅ **Table Sorting** - click column header to sort formats

✅ **Storyboard Filtering** - technical formats automatically hidden

✅ **Fast Download** - no re-encoding, only stream merging

✅ **Flexible Conversion** - full control over FFmpeg parameters

✅ **Modern UI** - clean interface with padding and hover effects

✅ **Bilingual Interface** - English/Russian language switcher

## 📁 Project Structure

```
video-extractor/
├── app.py                  # Main application window
├── download_tab.py         # YouTube download module
├── convert_tab.py          # Video conversion module
├── utils.py                # Common utilities
├── translations.py         # Localization system
├── ytdlp_wrapper.py        # yt-dlp wrapper module
├── create_release.py       # Automated release builder
├── download_binaries.py    # Binary downloader script
├── bin/                    # External binaries (auto-downloaded)
│   ├── ffmpeg.exe          # Video/audio processing
│   ├── yt-dlp.exe          # YouTube downloader
│   └── node.exe            # JavaScript runtime
├── assets/                 # Application assets
│   └── icons/              # Application icons
│       ├── icon.ico        # Main application icon
│       ├── refresh.ico     # Update button icon
│       └── download-btn.ico # Download button icon
├── requirements.txt        # Python dependencies
├── VideoExtractorByParallaXYZ.spec   # PyInstaller configuration
├── build.bat               # Build script
├── .gitignore              # Git ignore rules
├── LICENSE.md              # License
├── ABOUT.md                # About the project
└── README.md               # Documentation
```

## 🔧 Technical Details

### Technologies Used
- **PyQt5** - GUI framework
- **yt-dlp** - YouTube download
- **FFmpeg** - video processing and conversion
- **Microsoft Edge** - authorization via cookies
- **Node.js** - JavaScript challenge solving

### Data Storage
- Edge Profile: `%LOCALAPPDATA%\Video Extractor by ParallaXYZ\edge_profile`
- Downloaded Files: `%USERPROFILE%\Downloads` (default)

### Multithreading
All operations (analysis, download, conversion) run in separate threads, keeping UI responsive.

## ❓ FAQ

**Q: Why is authorization needed?**  
A: To access Premium formats (720p50, 1080p50, 4K) and private videos.

**Q: Is authorization safe?**  
A: Yes, it uses an isolated Edge profile that doesn't affect your main browser.

**Q: Can I download without authorization?**  
A: No, the "Analyze" button will be disabled until authorization.

**Q: Why don't I see some formats?**  
A: Make sure you're signed in to a YouTube Premium account to access high-quality formats.

**Q: How to change save folder?**  
A: Click "Change folder..." at the bottom of the window.

**Q: What to do with "Profile Locked" error?**  
A: Close all Edge windows and try again.

## 🐛 Troubleshooting

### Video analysis error
1. Make sure Edge is closed
2. Check internet connection
3. Try authorizing again

### Video won't download
1. Check that format is selected in the table
2. Make sure you have disk space
3. Check folder access permissions

### Conversion error
1. Make sure FFmpeg is installed
2. Check that input file is not corrupted
3. Try different codec parameters

## 📝 License

See [LICENSE.md](LICENSE.md) file

**Important:** Commercial use is PROHIBITED without written permission.

## 👤 Author

**ParallaXYZ**

- 💬 Discord: `parallaxyz`
- 🐙 GitHub: [@ParallaXYZ](https://github.com/ParallaXYZ)

Created for personal use. More details in [ABOUT.md](ABOUT.md)

---

**Version:** 1.0  
**Last Updated:** 2026-06-21
