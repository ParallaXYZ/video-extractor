# download_tab.py
"""Модуль скачивания видео с YouTube by ParallaXYZ"""

import os
import threading
import traceback
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon

from utils import (
    EDGE_PROFILE_DIR, 
    human_size, 
    classify, 
    parse_percent,
    is_cookie_error,
    resource_path
)
from ytdlp_wrapper import extract_info, download_video, download_audio
from translations import translator


class DownloadTab(QtWidgets.QWidget):
    """Tab for downloading videos from YouTube"""
    
    # Signals for updating UI from threads
    update_progress_signal = QtCore.pyqtSignal(int, str)
    set_busy_signal = QtCore.pyqtSignal(bool, str)
    mark_done_signal = QtCore.pyqtSignal()
    show_cookie_error_signal = QtCore.pyqtSignal()
    
    def __init__(self, parent=None, default_dir="", button_style=""):
        super().__init__(parent)
        self.default_dir = default_dir
        self.button_style = button_style
        self.info = None
        self.formats = []
        self.current_download_dir = default_dir
        
        self._init_ui()
        self._connect_signals()
    
    def _init_ui(self):
        """Initialize tab UI"""
        # Filters
        self.filterGroup = QtWidgets.QButtonGroup(self)
        self.rbAll = QtWidgets.QRadioButton(translator.tr('filter_all'))
        self.rbVideo = QtWidgets.QRadioButton(translator.tr('filter_video'))
        self.rbAudio = QtWidgets.QRadioButton(translator.tr('filter_audio'))
        self.rbMuxed = QtWidgets.QRadioButton(translator.tr('filter_muxed'))
        
        for rb in (self.rbAll, self.rbVideo, self.rbAudio, self.rbMuxed):
            self.filterGroup.addButton(rb)
        self.rbAll.setChecked(True)
        
        # Format table
        self.table = QtWidgets.QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            translator.tr('header_type'),
            translator.tr('header_container'),
            translator.tr('header_resolution'),
            translator.tr('header_fps'),
            translator.tr('header_size'),
            translator.tr('header_codecs')
        ])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        
        # Disable Qt built-in sorting (it sorts by text, not numbers)
        self.table.setSortingEnabled(False)
        self.table.horizontalHeader().setSortIndicatorShown(True)
        self.table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        
        # Store current sort column and order
        self.current_sort_column = -1
        self.current_sort_order = QtCore.Qt.AscendingOrder
        
        # Download button
        self.downloadBtn = QtWidgets.QPushButton(translator.tr('download_selected'))
        download_icon_path = resource_path('assets/icons/download-btn.ico')
        if os.path.exists(download_icon_path):
            self.downloadBtn.setIcon(QIcon(download_icon_path))
            self.downloadBtn.setIconSize(QtCore.QSize(20, 20))
        
        # Layout
        filter_layout = QtWidgets.QHBoxLayout()
        for rb in (self.rbAll, self.rbVideo, self.rbAudio, self.rbMuxed):
            filter_layout.addWidget(rb)
        filter_layout.addStretch(1)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self.table, 1)
        main_layout.addWidget(self.downloadBtn)
    
    def _connect_signals(self):
        """Connect signals"""
        self.filterGroup.buttonClicked.connect(self.apply_filter)
        self.downloadBtn.clicked.connect(self.on_download)
    
    def set_download_dir(self, directory):
        """Set download directory"""
        self.current_download_dir = directory
    
    def analyze_url(self, url):
        """Analyze URL in separate thread"""
        self.info = None
        self.formats = []
        self.table.setRowCount(0)
        threading.Thread(target=self._analyze_worker, args=(url,), daemon=True).start()
    
    def _analyze_worker(self, url):
        """Worker thread for video analysis"""
        try:
            # Extract video info using yt-dlp.exe
            info = extract_info(url, EDGE_PROFILE_DIR, download=False)
            
            self.info = info
            self.formats = info.get("formats", [])
            
            # Update table in main thread
            QtCore.QMetaObject.invokeMethod(
                self, "_populate_table", QtCore.Qt.QueuedConnection
            )
            
            # Clear busy state and show success
            self.set_busy_signal.emit(False, translator.tr('formats_found').format(len(self.formats)))
            
        except Exception as e:
            tb = traceback.format_exc()
            print(tb)
            error_msg = str(e) + "\n" + tb
            
            if is_cookie_error(error_msg):
                self.show_cookie_error_signal.emit()
            
            # Clear busy state on error
            self.set_busy_signal.emit(False, translator.tr('analysis_error'))
            
            QtCore.QMetaObject.invokeMethod(
                self, "_show_error", QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, str(e))
            )
    
    @QtCore.pyqtSlot()
    def _populate_table(self):
        """Fill table with formats"""
        rows = []
        for f in self.formats:
            # Skip technical storyboard formats
            if f.get('format_id', '').startswith('sb') or f.get('ext') == 'mhtml':
                continue
            
            typ = classify(f)
            
            # For sorting, save numeric value of resolution/bitrate
            if typ != "audio":
                resolution_text = f"{f.get('width', '?')}x{f.get('height', '?')}"
                resolution_value = f.get('width', 0) or 0  # Sort by width
            else:
                abr = f.get('abr', 0) or 0
                resolution_text = f"{abr} kbps"
                resolution_value = abr  # Sort by bitrate
            
            rows.append({
                "type": typ,
                "ext": f.get("ext", ""),
                "desc": resolution_text,
                "desc_value": resolution_value,  # Numeric value for sorting
                "fps": str(f.get("fps", "")) if f.get("fps") else "",
                "size": f.get("filesize") or f.get("filesize_approx") or 0,
                "codecs": f"{f.get('vcodec', 'none')}/{f.get('acodec', 'none')}",
                "format_id": f.get("format_id", ""),  # Save for download
            })
        
        self.all_rows = rows
        self.apply_filter()
    
    def apply_filter(self):
        """Apply filter to table"""
        if not hasattr(self, 'all_rows'):
            return
        
        filter_type = None
        if self.rbVideo.isChecked():
            filter_type = "video"
        elif self.rbAudio.isChecked():
            filter_type = "audio"
        elif self.rbMuxed.isChecked():
            filter_type = "muxed"
        
        filtered = [r for r in self.all_rows if filter_type is None or r["type"] == filter_type]
        
        self.table.setRowCount(len(filtered))
        for row, r in enumerate(filtered):
            # Create items with correct data for sorting
            type_item = QtWidgets.QTableWidgetItem(r["type"])
            ext_item = QtWidgets.QTableWidgetItem(r["ext"])
            
            # For resolution/bitrate save numeric value for sorting
            desc_item = QtWidgets.QTableWidgetItem(r["desc"])
            desc_item.setData(QtCore.Qt.UserRole, r["desc_value"])  # Numeric value
            
            fps_item = QtWidgets.QTableWidgetItem(r["fps"])
            
            # For size save numeric value for sorting
            size_item = QtWidgets.QTableWidgetItem(human_size(r["size"]))
            size_item.setData(QtCore.Qt.UserRole, r["size"])  # Save numeric value
            
            codecs_item = QtWidgets.QTableWidgetItem(r["codecs"])
            
            # Save format_id in first cell (hidden from user)
            type_item.setData(QtCore.Qt.UserRole, r["format_id"])
            
            self.table.setItem(row, 0, type_item)
            self.table.setItem(row, 1, ext_item)
            self.table.setItem(row, 2, desc_item)
            self.table.setItem(row, 3, fps_item)
            self.table.setItem(row, 4, size_item)
            self.table.setItem(row, 5, codecs_item)
    
    def on_header_clicked(self, logical_index):
        """Handle header click for sorting"""
        # Determine sort order
        if self.current_sort_column == logical_index:
            # Click on same column - change order
            if self.current_sort_order == QtCore.Qt.AscendingOrder:
                self.current_sort_order = QtCore.Qt.DescendingOrder
            else:
                self.current_sort_order = QtCore.Qt.AscendingOrder
        else:
            # Click on new column - start with descending for numeric, ascending for text
            self.current_sort_column = logical_index
            if logical_index in [2, 4]:  # Resolution/Bitrate and Size
                self.current_sort_order = QtCore.Qt.DescendingOrder  # Larger values first
            else:
                self.current_sort_order = QtCore.Qt.AscendingOrder   # A-Z first
        
        # Update sort indicator
        self.table.horizontalHeader().setSortIndicator(logical_index, self.current_sort_order)
        
        # Collect data for sorting
        rows_data = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, logical_index)
            
            # For numeric columns use UserRole, for text - text
            if logical_index in [2, 4]:  # Resolution/Bitrate and Size
                value = item.data(QtCore.Qt.UserRole) if item else 0
            else:
                value = item.text() if item else ""
            
            rows_data.append((row, value))
        
        # Sort
        reverse = (self.current_sort_order == QtCore.Qt.DescendingOrder)
        rows_data.sort(key=lambda x: x[1], reverse=reverse)
        
        # Rebuild table
        sorted_rows = []
        for _, _ in rows_data:
            sorted_rows.append([])
        
        for new_row, (old_row, _) in enumerate(rows_data):
            for col in range(self.table.columnCount()):
                item = self.table.item(old_row, col)
                if item:
                    sorted_rows[new_row].append(item.clone())
                else:
                    sorted_rows[new_row].append(QtWidgets.QTableWidgetItem(""))
        
        for row_idx, row_items in enumerate(sorted_rows):
            for col_idx, item in enumerate(row_items):
                self.table.setItem(row_idx, col_idx, item)
    
    def selected_format(self):
        """Get selected format"""
        r = self.table.currentRow()
        if r < 0:
            return None
        
        # format_id saved in UserRole of first cell
        type_item = self.table.item(r, 0)
        format_id = type_item.data(QtCore.Qt.UserRole) if type_item else ""
        
        return {
            "id": format_id,
            "type": self.table.item(r, 0).text(),
            "ext": self.table.item(r, 1).text(),
            "desc": self.table.item(r, 2).text(),
        }
    
    def on_download(self):
        """Download button handler"""
        sel = self.selected_format()
        if not sel:
            QMessageBox.warning(self, translator.tr('error'), translator.tr('no_format_selected'))
            return
        if not self.info:
            QMessageBox.warning(self, translator.tr('error'), translator.tr('analyze_first'))
            return
        
        outdir = self.current_download_dir
        os.makedirs(outdir, exist_ok=True)
        
        self.set_busy_signal.emit(True, translator.tr('downloading'))
        threading.Thread(target=self._download_worker, args=(sel, outdir), daemon=True).start()
    
    def _download_worker(self, sel, outdir):
        """Download worker thread"""
        try:
            url = self.info.get("webpage_url") or self.info.get("original_url")
            base_tmpl = os.path.join(outdir, "%(title)s-%(id)s.%(ext)s")
            
            # Progress callback
            def progress_callback(percent, message):
                try:
                    if percent is not None:
                        self.update_progress_signal.emit(int(percent), f"{percent:.1f}%")
                    else:
                        # Status message (merging, post-processing, etc.)
                        if 'Merging' in message or 'Post-processing' in message or 'Extracting' in message:
                            self.set_busy_signal.emit(True, translator.tr('processing'))
                except Exception:
                    pass
            
            # Download based on type
            if sel["type"] == "audio":
                # Download and extract audio
                download_audio(url, EDGE_PROFILE_DIR, base_tmpl, progress_callback)
            else:
                # Download video
                format_spec = "bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/bestvideo*+bestaudio/best"
                download_video(url, EDGE_PROFILE_DIR, base_tmpl, format_spec, progress_callback)
            
            self.mark_done_signal.emit()
            self.set_busy_signal.emit(False, translator.tr('saved_to').format(outdir))
            
        except Exception as e:
            tb = traceback.format_exc()
            print(tb)
            error_msg = str(e) + "\n" + tb
            
            if is_cookie_error(error_msg):
                self.show_cookie_error_signal.emit()
            
            self.set_busy_signal.emit(False, translator.tr('error').format(e))
            self.update_progress_signal.emit(0, translator.tr('error'))
    
    @QtCore.pyqtSlot(str)
    def _show_error(self, error):
        """Show error"""
        QMessageBox.critical(self, translator.tr('analysis_error'), f"Failed to analyze video:\n\n{error}")
    
    def refresh_ui(self):
        """Refresh UI with current language"""
        # Update filter buttons
        self.rbAll.setText(translator.tr('filter_all'))
        self.rbVideo.setText(translator.tr('filter_video'))
        self.rbAudio.setText(translator.tr('filter_audio'))
        self.rbMuxed.setText(translator.tr('filter_muxed'))
        
        # Update table headers
        self.table.setHorizontalHeaderLabels([
            translator.tr('header_type'),
            translator.tr('header_container'),
            translator.tr('header_resolution'),
            translator.tr('header_fps'),
            translator.tr('header_size'),
            translator.tr('header_codecs')
        ])
        
        # Update download button
        self.downloadBtn.setText(translator.tr('download_selected'))
