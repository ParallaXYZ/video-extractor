# convert_tab.py
"""Offline video conversion module"""

import os
import subprocess
import threading
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from translations import translator


class ConvertTab(QtWidgets.QWidget):
    """Tab for converting local video files"""
    
    # Signals
    update_progress_signal = QtCore.pyqtSignal(int, str)
    set_busy_signal = QtCore.pyqtSignal(bool, str)
    
    def __init__(self, parent=None, button_style="", ffmpeg_location=""):
        super().__init__(parent)
        self.button_style = button_style
        self.ffmpeg_location = ffmpeg_location
        self.input_file = None
        self.output_file = None
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI"""
        # Title
        self.titleLabel = QtWidgets.QLabel(translator.tr('convert_title'))
        self.titleLabel.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        
        # Input file selection
        self.inputLabel = QtWidgets.QLabel(translator.tr('input_file_not_selected'))
        self.inputLabel.setWordWrap(True)
        self.selectInputBtn = QtWidgets.QPushButton(translator.tr('select_video_file'))
        self.selectInputBtn.clicked.connect(self.select_input_file)
        
        self.inputGroup = QtWidgets.QGroupBox(translator.tr('select_file_group'))
        input_layout = QtWidgets.QVBoxLayout()
        input_layout.addWidget(self.inputLabel)
        input_layout.addWidget(self.selectInputBtn)
        self.inputGroup.setLayout(input_layout)
        
        # Conversion settings
        self.settingsGroup = QtWidgets.QGroupBox(translator.tr('conversion_settings_group'))
        settings_layout = QtWidgets.QFormLayout()
        
        # Video codec
        self.videoCodecCombo = QtWidgets.QComboBox()
        self.videoCodecCombo.addItems([
            translator.tr('codec_h264'),
            translator.tr('codec_h265'),
            translator.tr('codec_copy')
        ])
        self.videoCodecLabel = QtWidgets.QLabel(translator.tr('video_codec'))
        settings_layout.addRow(self.videoCodecLabel, self.videoCodecCombo)
        
        # Audio codec
        self.audioCodecCombo = QtWidgets.QComboBox()
        self.audioCodecCombo.addItems([
            translator.tr('codec_aac'),
            translator.tr('codec_mp3'),
            translator.tr('codec_copy')
        ])
        self.audioCodecLabel = QtWidgets.QLabel(translator.tr('audio_codec'))
        settings_layout.addRow(self.audioCodecLabel, self.audioCodecCombo)
        
        # Video quality (CRF)
        self.crfSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.crfSlider.setMinimum(18)
        self.crfSlider.setMaximum(28)
        self.crfSlider.setValue(23)
        self.crfSlider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.crfSlider.setTickInterval(2)
        self.crfLabel = QtWidgets.QLabel(translator.tr('crf_balanced').format(23))
        self.crfLabel.setFixedWidth(100)  # Fixed width to prevent jumping
        self.crfLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.crfSlider.valueChanged.connect(self.update_crf_label)
        
        crf_layout = QtWidgets.QHBoxLayout()
        crf_layout.addWidget(self.crfSlider)
        crf_layout.addWidget(self.crfLabel)
        self.qualityCrfLabel = QtWidgets.QLabel(translator.tr('quality_crf'))
        settings_layout.addRow(self.qualityCrfLabel, crf_layout)
        
        # Audio bitrate
        self.audioBitrateCombo = QtWidgets.QComboBox()
        self.audioBitrateCombo.addItems(["128k", "192k", "256k", "320k"])
        self.audioBitrateCombo.setCurrentText("192k")
        self.audioBitrateLabel = QtWidgets.QLabel(translator.tr('audio_bitrate'))
        settings_layout.addRow(self.audioBitrateLabel, self.audioBitrateCombo)
        
        # Container
        self.containerCombo = QtWidgets.QComboBox()
        self.containerCombo.addItems(["mp4", "mkv", "avi", "webm"])
        self.containerLabel = QtWidgets.QLabel(translator.tr('container'))
        settings_layout.addRow(self.containerLabel, self.containerCombo)
        
        self.settingsGroup.setLayout(settings_layout)
        
        # Output file selection
        self.outputLabel = QtWidgets.QLabel(translator.tr('output_file_auto'))
        self.outputLabel.setWordWrap(True)
        self.selectOutputBtn = QtWidgets.QPushButton(translator.tr('change_save_path'))
        self.selectOutputBtn.clicked.connect(self.select_output_file)
        
        self.outputGroup = QtWidgets.QGroupBox(translator.tr('save_group'))
        output_layout = QtWidgets.QVBoxLayout()
        output_layout.addWidget(self.outputLabel)
        output_layout.addWidget(self.selectOutputBtn)
        self.outputGroup.setLayout(output_layout)
        
        # Convert button
        self.convertBtn = QtWidgets.QPushButton(translator.tr('start_conversion'))
        self.convertBtn.clicked.connect(self.start_conversion)
        self.convertBtn.setEnabled(False)
        
        # Information
        self.infoLabel = QtWidgets.QLabel(translator.tr('conversion_hints'))
        self.infoLabel.setWordWrap(True)
        self.infoLabel.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px; margin-top: 10px;")
        
        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.titleLabel)
        main_layout.addWidget(self.inputGroup)
        main_layout.addWidget(self.settingsGroup)
        main_layout.addWidget(self.outputGroup)
        main_layout.addWidget(self.convertBtn)
        main_layout.addWidget(self.infoLabel)
        main_layout.addStretch(1)
    
    def update_crf_label(self, value):
        """Update CRF label"""
        quality_map = {
            18: translator.tr('crf_excellent').format(18),
            20: translator.tr('crf_very_good').format(20),
            23: translator.tr('crf_balanced').format(23),
            26: translator.tr('crf_acceptable').format(26),
            28: translator.tr('crf_low').format(28)
        }
        label = quality_map.get(value, f"{value}")
        self.crfLabel.setText(label)
    
    def select_input_file(self):
        """Select input file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            translator.tr('select_video_file'),
            "",
            "Video files (*.mp4 *.mkv *.avi *.webm *.mov *.flv *.wmv);;All files (*.*)"
        )
        
        if file_path:
            self.input_file = file_path
            self.inputLabel.setText(translator.tr('input_file').format(os.path.basename(file_path)))
            
            # Automatically generate output file
            base_name = os.path.splitext(file_path)[0]
            container = self.containerCombo.currentText()
            self.output_file = f"{base_name}_converted.{container}"
            self.outputLabel.setText(translator.tr('output_file').format(os.path.basename(self.output_file)))
            
            self.convertBtn.setEnabled(True)
    
    def select_output_file(self):
        """Select output file"""
        if not self.input_file:
            QMessageBox.warning(self, translator.tr('error'), translator.tr('select_input_first'))
            return
        
        container = self.containerCombo.currentText()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            translator.tr('change_save_path'),
            self.output_file or "",
            f"Video {container.upper()} (*.{container});;All files (*.*)"
        )
        
        if file_path:
            self.output_file = file_path
            self.outputLabel.setText(translator.tr('output_file').format(os.path.basename(file_path)))
    
    def start_conversion(self):
        """Start conversion"""
        if not self.input_file or not self.output_file:
            QMessageBox.warning(self, translator.tr('error'), translator.tr('select_input_first'))
            return
        
        # Confirmation
        reply = QMessageBox.question(
            self,
            translator.tr('confirm_conversion_title'),
            translator.tr('confirm_conversion_message').format(
                os.path.basename(self.input_file),
                os.path.basename(self.output_file)
            ),
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.set_busy_signal.emit(True, translator.tr('converting'))
            threading.Thread(target=self._convert_worker, daemon=True).start()
    
    def _convert_worker(self):
        """Conversion worker thread"""
        try:
            # Get parameters
            video_codec_map = {
                translator.tr('codec_h264'): "libx264",
                translator.tr('codec_h265'): "libx265",
                translator.tr('codec_copy'): "copy"
            }
            audio_codec_map = {
                translator.tr('codec_aac'): "aac",
                translator.tr('codec_mp3'): "libmp3lame",
                translator.tr('codec_copy'): "copy"
            }
            
            video_codec = video_codec_map[self.videoCodecCombo.currentText()]
            audio_codec = audio_codec_map[self.audioCodecCombo.currentText()]
            crf = self.crfSlider.value()
            audio_bitrate = self.audioBitrateCombo.currentText()
            
            # Build ffmpeg command
            ffmpeg_exe = os.path.join(self.ffmpeg_location, "ffmpeg.exe") if self.ffmpeg_location else "ffmpeg"
            
            cmd = [
                ffmpeg_exe,
                "-i", self.input_file,
                "-c:v", video_codec,
            ]
            
            # Add CRF only if not copy
            if video_codec != "copy":
                cmd.extend(["-crf", str(crf)])
                cmd.extend(["-preset", "medium"])
                cmd.extend(["-pix_fmt", "yuv420p"])
            
            cmd.extend(["-c:a", audio_codec])
            
            if audio_codec != "copy":
                cmd.extend(["-b:a", audio_bitrate])
            
            cmd.extend(["-y", self.output_file])
            
            print(f"FFmpeg command: {' '.join(cmd)}")
            
            # Start process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            # Read output
            for line in process.stdout:
                print(line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                self.set_busy_signal.emit(False, translator.tr('conversion_complete'))
                QtCore.QMetaObject.invokeMethod(
                    self, "_show_success", QtCore.Qt.QueuedConnection
                )
            else:
                self.set_busy_signal.emit(False, translator.tr('conversion_error'))
                QtCore.QMetaObject.invokeMethod(
                    self, "_show_error", QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(str, f"FFmpeg returned error code: {process.returncode}")
                )
                
        except Exception as e:
            self.set_busy_signal.emit(False, translator.tr('conversion_error'))
            QtCore.QMetaObject.invokeMethod(
                self, "_show_error", QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, str(e))
            )
    
    @QtCore.pyqtSlot()
    def _show_success(self):
        """Show success"""
        QMessageBox.information(
            self,
            translator.tr('conversion_done_title'),
            translator.tr('conversion_done_message').format(self.output_file)
        )
    
    @QtCore.pyqtSlot(str)
    def _show_error(self, error):
        """Show error"""
        QMessageBox.critical(
            self,
            translator.tr('conversion_error_title'),
            translator.tr('conversion_error_message').format(error)
        )
    
    def refresh_ui(self):
        """Refresh UI with current language"""
        # Update title and groups
        self.titleLabel.setText(translator.tr('convert_title'))
        self.inputGroup.setTitle(translator.tr('select_file_group'))
        self.settingsGroup.setTitle(translator.tr('conversion_settings_group'))
        self.outputGroup.setTitle(translator.tr('save_group'))
        
        # Update field labels
        self.videoCodecLabel.setText(translator.tr('video_codec'))
        self.audioCodecLabel.setText(translator.tr('audio_codec'))
        self.qualityCrfLabel.setText(translator.tr('quality_crf'))
        self.audioBitrateLabel.setText(translator.tr('audio_bitrate'))
        self.containerLabel.setText(translator.tr('container'))
        
        # Update combo box items
        self.videoCodecCombo.clear()
        self.videoCodecCombo.addItems([
            translator.tr('codec_h264'),
            translator.tr('codec_h265'),
            translator.tr('codec_copy')
        ])
        
        self.audioCodecCombo.clear()
        self.audioCodecCombo.addItems([
            translator.tr('codec_aac'),
            translator.tr('codec_mp3'),
            translator.tr('codec_copy')
        ])
        
        # Update buttons
        self.selectInputBtn.setText(translator.tr('select_video_file'))
        self.selectOutputBtn.setText(translator.tr('change_save_path'))
        self.convertBtn.setText(translator.tr('start_conversion'))
        
        # Update info
        self.infoLabel.setText(translator.tr('conversion_hints'))
        
        # Update CRF label
        self.update_crf_label(self.crfSlider.value())
        
        # Update labels
        if not self.input_file:
            self.inputLabel.setText(translator.tr('input_file_not_selected'))
        else:
            self.inputLabel.setText(translator.tr('input_file').format(os.path.basename(self.input_file)))
        
        if not self.output_file:
            self.outputLabel.setText(translator.tr('output_file_auto'))
        else:
            self.outputLabel.setText(translator.tr('output_file').format(os.path.basename(self.output_file)))
