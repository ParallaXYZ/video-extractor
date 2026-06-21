# app.py
"""Main window Video extractor by ParallaXYZ"""

import sys
import os
import subprocess
import urllib.request
import shutil
import tempfile
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QProgressBar, QMessageBox, QFrame, QLabel
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QIcon

from utils import (
    APP_NAME,
    DEFAULT_DIR,
    check_edge_auth,
    open_auth_edge,
    ensure_edge_profile_dir,
    ffmpeg_dir,
    resource_path,
    ytdlp_path
)
from download_tab import DownloadTab
from convert_tab import ConvertTab
from translations import translator


class UpdateWorker(QThread):
    """Worker thread for updating yt-dlp.exe"""
    finished = pyqtSignal(bool, str)  # success, message
    progress = pyqtSignal(int)  # download progress
    
    def run(self):
        try:
            # Get path to yt-dlp.exe in bin directory
            ytdlp_exe = ytdlp_path()
            bin_dir = os.path.dirname(ytdlp_exe)
            
            # Ensure bin directory exists
            os.makedirs(bin_dir, exist_ok=True)
            
            # Get current version
            old_version = 'unknown'
            if os.path.exists(ytdlp_exe):
                try:
                    result = subprocess.run(
                        [ytdlp_exe, '--version'],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                    )
                    if result.returncode == 0:
                        old_version = result.stdout.strip()
                except:
                    pass
            
            # Download new version from GitHub
            download_url = 'https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe'
            
            # Create temporary file in bin directory
            temp_path = os.path.join(bin_dir, 'yt-dlp.new.exe')
            
            try:
                # Download with progress
                def reporthook(block_num, block_size, total_size):
                    if total_size > 0:
                        percent = min(int(block_num * block_size * 100 / total_size), 100)
                        self.progress.emit(percent)
                
                urllib.request.urlretrieve(download_url, temp_path, reporthook=reporthook)
                
                # Verify downloaded file works
                new_version = 'unknown'
                try:
                    result = subprocess.run(
                        [temp_path, '--version'],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                    )
                    if result.returncode == 0:
                        new_version = result.stdout.strip()
                    else:
                        raise Exception("Downloaded yt-dlp.exe failed to run")
                except Exception as e:
                    # Clean up invalid download
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                    raise Exception(f"Downloaded file verification failed: {e}")
                
                # Check if update needed
                if old_version == new_version and old_version != 'unknown':
                    os.unlink(temp_path)
                    self.finished.emit(True, f'up_to_date:{new_version}')
                    return
                
                # Replace old file with new one
                if os.path.exists(ytdlp_exe):
                    os.unlink(ytdlp_exe)
                shutil.move(temp_path, ytdlp_exe)
                
                self.finished.emit(True, f'updated:{new_version}')
                
            except Exception as e:
                # Clean up temp file on error
                if os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                raise e
                
        except Exception as e:
            self.finished.emit(False, str(e))


class MainWindow(QtWidgets.QWidget):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(980, 700)
        self.current_dir = DEFAULT_DIR
        
        # Set window icon
        icon_path = resource_path('assets/icons/icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Button style
        self.button_style = "padding-left: 12px; padding-right: 12px;"
        
        # Update worker
        self.update_worker = None
        
        self._init_ui()
        self._connect_signals()
        
        # Create profile folder and check authorization
        ensure_edge_profile_dir()
        self.update_auth_state()
        self.reset_progress("")
        
        # Show tooltip on startup
        QtCore.QTimer.singleShot(500, self.show_startup_tooltip)
    
    def _init_ui(self):
        """Initialize UI"""
        # Top panel (URL + buttons)
        self.urlEdit = QtWidgets.QLineEdit()
        self.urlEdit.setPlaceholderText(translator.tr('url_placeholder'))
        
        self.analyzeBtn = QtWidgets.QPushButton(translator.tr('analyze'))
        self.authBtn = QtWidgets.QPushButton(translator.tr('auth_edge'))
        
        # Language switcher - shows CURRENT language
        current_lang = translator.get_language()
        self.langBtn = QtWidgets.QPushButton(f"🌐 {current_lang.upper()}")
        self.langBtn.setToolTip("Switch language / Переключить язык")
        self.langBtn.clicked.connect(self.toggle_language)
        
        # Update button
        self.updateBtn = QtWidgets.QPushButton(translator.tr('update_ytdlp_text'))
        refresh_icon_path = resource_path('assets/icons/refresh.ico')
        if os.path.exists(refresh_icon_path):
            self.updateBtn.setIcon(QIcon(refresh_icon_path))
            self.updateBtn.setIconSize(QtCore.QSize(20, 20))
        self.updateBtn.setToolTip(translator.tr('update_ytdlp'))
        self.updateBtn.clicked.connect(self.on_update_ytdlp)
        
        # Create tabs
        self.tabs = QtWidgets.QTabWidget()
        
        # Download tab
        self.download_tab = DownloadTab(
            parent=self,
            default_dir=DEFAULT_DIR,
            button_style=self.button_style
        )
        
        # Convert tab
        self.convert_tab = ConvertTab(
            parent=self,
            button_style=self.button_style,
            ffmpeg_location=ffmpeg_dir()
        )
        
        self.tabs.addTab(self.download_tab, translator.tr('tab_download'))
        self.tabs.addTab(self.convert_tab, translator.tr('tab_convert'))
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setTextVisible(True)
        self.progress.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self._default_progress_css = ""
        
        # Save path
        self.pathLbl = QtWidgets.QLabel(f"{translator.tr('folder')}: {DEFAULT_DIR}")
        self.chooseDirBtn = QtWidgets.QPushButton(translator.tr('change_folder'))
        
        # Status bar
        self.status = QtWidgets.QStatusBar()
        
        # Tooltip notification (initially hidden)
        self.tooltip_frame = QFrame()
        self.tooltip_frame.setFrameShape(QFrame.StyledPanel)
        self.tooltip_frame.setStyleSheet("""
            QFrame {
                background-color: #fff3cd;
                border: 1px solid #ffc107;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        tooltip_layout = QtWidgets.QHBoxLayout(self.tooltip_frame)
        tooltip_layout.setContentsMargins(8, 8, 8, 8)
        
        self.tooltip_label = QLabel()
        self.tooltip_label.setWordWrap(True)
        self.tooltip_label.setStyleSheet("background: transparent; border: none; color: #856404;")
        
        self.tooltip_close_btn = QtWidgets.QPushButton("✕")
        self.tooltip_close_btn.setFixedSize(20, 20)
        self.tooltip_close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #856404;
                font-weight: bold;
                padding: 0;
            }
            QPushButton:hover {
                color: #533f03;
            }
        """)
        self.tooltip_close_btn.clicked.connect(lambda: self.tooltip_frame.hide())
        
        tooltip_layout.addWidget(self.tooltip_label, 1)
        tooltip_layout.addWidget(self.tooltip_close_btn)
        self.tooltip_frame.hide()  # Hidden by default
        
        # Main layout
        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(self.urlEdit, 1)
        top_layout.addWidget(self.analyzeBtn)
        top_layout.addWidget(self.authBtn)
        top_layout.addWidget(self.langBtn)
        top_layout.addWidget(self.updateBtn)
        
        path_layout = QtWidgets.QHBoxLayout()
        path_layout.addWidget(self.pathLbl, 1)
        path_layout.addWidget(self.chooseDirBtn)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.tooltip_frame)  # Tooltip notification
        main_layout.addWidget(self.tabs, 1)
        main_layout.addWidget(self.progress)
        main_layout.addLayout(path_layout)
        main_layout.addWidget(self.status)
        
        # Global styles for buttons and input fields(activate padding)
        self.setStyleSheet("""
            QPushButton {
                border: 1px solid #b0b0b0;
                border-radius: 4px;
                background-color: #f5f5f5;
                padding: 6px 16px;
                min-height: 18px;
            }
            QPushButton:hover {
                background-color: #e5e5e5;
            }
            QPushButton:pressed {
                background-color: #d5d5d5;
            }
            QPushButton:disabled {
                background-color: #e0e0e0;
                color: #a0a0a0;
            }
            QLineEdit {
                border: 1px solid #b0b0b0;
                border-radius: 4px;
                padding: 6px 12px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #0078d4;
            }
            QComboBox {
                border: 1px solid #b0b0b0;
                border-radius: 4px;
                padding: 4px 8px;
                background-color: white;
            }
            QRadioButton {
                padding: 4px 8px;
            }
        """)
    
    def _connect_signals(self):
        """Connect signals"""
        self.analyzeBtn.clicked.connect(self.on_analyze)
        self.authBtn.clicked.connect(self.on_auth_edge)
        self.chooseDirBtn.clicked.connect(self.on_choose_dir)
        
        # Signals from download tab
        self.download_tab.update_progress_signal.connect(self.update_progress)
        self.download_tab.set_busy_signal.connect(self.set_busy)
        self.download_tab.mark_done_signal.connect(self.mark_done_progress)
        self.download_tab.show_cookie_error_signal.connect(self.show_cookie_help_dialog)
        
        # Signals from convert tab
        self.convert_tab.update_progress_signal.connect(self.update_progress)
        self.convert_tab.set_busy_signal.connect(self.set_busy)
    
    def toggle_language(self):
        """Toggle between English and Russian"""
        current_lang = translator.get_language()
        new_lang = 'ru' if current_lang == 'en' else 'en'
        translator.set_language(new_lang)
        
        # Update language button to show NEW current language
        self.langBtn.setText(f"🌐 {new_lang.upper()}")
        
        # Refresh UI
        self.refresh_ui()
    
    def refresh_ui(self):
        """Refresh all UI elements with new language"""
        # Update buttons
        self.analyzeBtn.setText(translator.tr('analyze'))
        self.authBtn.setText(translator.tr('auth_edge'))
        self.chooseDirBtn.setText(translator.tr('change_folder'))
        self.updateBtn.setText(translator.tr('update_ytdlp_text'))
        self.updateBtn.setToolTip(translator.tr('update_ytdlp'))
        
        # Update placeholder
        self.urlEdit.setPlaceholderText(translator.tr('url_placeholder'))
        
        # Update tabs
        self.tabs.setTabText(0, translator.tr('tab_download'))
        self.tabs.setTabText(1, translator.tr('tab_convert'))
        
        # Update path label
        self.pathLbl.setText(f"{translator.tr('folder')}: {self.current_dir}")
        
        # Clear status bar to remove old language messages
        self.status.clearMessage()
        
        # Update tooltip if visible
        if self.tooltip_frame.isVisible():
            self.tooltip_label.setText(
                f"<b>{translator.tr('update_tooltip_title')}</b><br>{translator.tr('update_tooltip_message')}"
            )
        
        # Update download tab
        self.download_tab.refresh_ui()
        
        # Update convert tab
        self.convert_tab.refresh_ui()
        
        # Update auth state message
        self.update_auth_state()
    
    def update_auth_state(self):
        """Update button states based on authorization"""
        is_authorized = check_edge_auth()
        
        self.analyzeBtn.setEnabled(is_authorized)
        self.authBtn.setEnabled(not is_authorized)
    
    def on_auth_edge(self):
        """Authorization button handler"""
        result = QMessageBox.information(
            self,
            translator.tr('auth_title'),
            translator.tr('auth_message'),
            QMessageBox.Ok | QMessageBox.Cancel
        )
        
        if result == QMessageBox.Ok:
            open_auth_edge()
            
            QMessageBox.information(
                self,
                translator.tr('auth_complete_title'),
                translator.tr('auth_complete_message')
            )
            
            self.update_auth_state()
    
    def on_analyze(self):
        """Analyze button handler"""
        url = self.urlEdit.text().strip()
        if not url:
            QMessageBox.warning(self, translator.tr('error'), translator.tr('enter_url'))
            return
        
        self.set_busy(True, translator.tr('analyzing'))
        self.reset_progress(translator.tr('analyzing'))
        self.download_tab.analyze_url(url)
    
    def on_choose_dir(self):
        """Choose save folder"""
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self, translator.tr('change_folder'), self.current_dir
        )
        if directory:
            self.current_dir = directory
            self.pathLbl.setText(f"{translator.tr('folder')}: {directory}")
            self.download_tab.set_download_dir(directory)
    
    # ---------- UI helpers ----------
    def _add_padding(self, text):
        """Add left padding to progress bar text"""
        return f"   {text}" if text else text
    
    def reset_progress(self, text=""):
        """Reset progress bar"""
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFormat(self._add_padding(text) if text else self._add_padding("%p%"))
        self.progress.setStyleSheet(self._default_progress_css)
    
    @QtCore.pyqtSlot(int, str)
    def update_progress(self, value: int, text: str):
        """Update progress"""
        self.progress.setRange(0, 100)
        self.progress.setValue(value)
        self.progress.setFormat(self._add_padding(text))
    
    @QtCore.pyqtSlot(bool, str)
    def set_busy(self, busy: bool, message: str = ""):
        """Set busy state"""
        if busy:
            self.progress.setRange(0, 0)
            self.progress.setFormat(self._add_padding(message))
            self.analyzeBtn.setEnabled(False)
            self.download_tab.downloadBtn.setEnabled(False)
        else:
            self.progress.setRange(0, 100)
            self.progress.setValue(0)
            self.analyzeBtn.setEnabled(check_edge_auth())
            self.download_tab.downloadBtn.setEnabled(True)
            if message:
                self.status.showMessage(message)
    
    @QtCore.pyqtSlot()
    def mark_done_progress(self):
        """Mark completion"""
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.progress.setFormat(self._add_padding(translator.tr('done')))
        self.progress.setStyleSheet("QProgressBar::chunk { background-color: #4CAF50; }")
    
    @QtCore.pyqtSlot()
    def show_cookie_help_dialog(self):
        """Show cookie error dialog"""
        QMessageBox.warning(
            self,
            translator.tr('profile_locked_title'),
            translator.tr('profile_locked_message')
        )
        self.status.showMessage(translator.tr('close_edge_retry'))
    
    def show_startup_tooltip(self):
        """Show tooltip notification on startup"""
        self.tooltip_label.setText(
            f"<b>{translator.tr('update_tooltip_title')}</b><br>{translator.tr('update_tooltip_message')}"
        )
        self.tooltip_frame.show()
    
    def on_update_ytdlp(self):
        """Update yt-dlp"""
        if self.update_worker and self.update_worker.isRunning():
            return
        
        self.updateBtn.setEnabled(False)
        self.set_busy(True, "")
        
        self.update_worker = UpdateWorker()
        self.update_worker.finished.connect(self.on_update_finished)
        self.update_worker.start()
    
    @QtCore.pyqtSlot(bool, str)
    def on_update_finished(self, success, message):
        """Handle update completion"""
        self.updateBtn.setEnabled(True)
        self.set_busy(False)
        
        if success:
            if message.startswith('up_to_date:'):
                version = message.split(':', 1)[1]
                msg = translator.tr('update_not_needed').format(version)
                QMessageBox.information(
                    self,
                    translator.tr('update_complete_title'),
                    msg
                )
            else:
                version = message.split(':', 1)[1]
                msg = translator.tr('update_success').format(version)
                QMessageBox.information(
                    self,
                    translator.tr('update_complete_title'),
                    msg
                )
        else:
            msg = translator.tr('update_error').format(message)
            QMessageBox.warning(
                self,
                translator.tr('update_error_title'),
                msg
            )
        
        self.update_auth_state()


def main():
    """Application entry point"""
    # Fix for Windows taskbar icon
    if sys.platform == 'win32':
        import ctypes
        # Set AppUserModelID to make taskbar icon work properly
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('ParallaXYZ.VideoExtractor.1.0')
    
    app = QtWidgets.QApplication(sys.argv)
    
    # Set application icon for taskbar and task manager
    icon_path = resource_path('assets/icons/icon.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    # CRITICAL: Must be called BEFORE anything else in frozen app
    if sys.platform == 'win32':
        import multiprocessing
        multiprocessing.freeze_support()
    
    main()
