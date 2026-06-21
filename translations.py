# translations.py
"""Localization system for Video extractor by ParallaXYZ"""

TRANSLATIONS = {
    'en': {
        # Main window
        'app_name': 'Video extractor by ParallaXYZ',
        'analyze': 'Analyze',
        'auth_edge': 'Edge Authorization',
        'change_folder': 'Change folder...',
        'folder': 'Folder',
        'ready': 'Ready',
        
        # Tabs
        'tab_download': '📥 Download from YouTube',
        'tab_convert': '🔄 Convert Video',
        
        # Download tab
        'filter_all': 'All',
        'filter_video': 'Video',
        'filter_audio': 'Audio',
        'filter_muxed': 'Combined',
        'download_selected': 'Download selected',
        
        # Table headers
        'header_type': 'Type',
        'header_container': 'Container',
        'header_resolution': 'Resolution/Bitrate',
        'header_fps': 'FPS',
        'header_size': 'Size',
        'header_codecs': 'Codecs',
        
        # Format types
        'type_video': 'video',
        'type_audio': 'audio',
        'type_muxed': 'muxed',
        
        # Messages
        'auth_required': '⚠ Authorization required. Click "Edge Authorization".',
        'auth_detected': '✓ Authorization detected. You can analyze videos.',
        'analyzing': 'Analyzing video...',
        'formats_found': '✓ Found formats: {}',
        'analysis_error': '✗ Analysis error',
        'downloading': 'Downloading...',
        'processing': 'Processing...',
        'done': 'Done',
        'saved_to': 'Done. Saved to: {}',
        'error': 'Error: {}',
        
        # Dialogs
        'auth_title': 'Edge Authorization',
        'auth_message': (
            'Microsoft Edge window will open with isolated profile.\n\n'
            '1. Sign in to your YouTube account\n'
            '2. Close Edge window after signing in\n'
            '3. Click OK in this window after closing Edge\n\n'
            'IMPORTANT: Close Edge before downloading!'
        ),
        'auth_complete_title': 'Complete Authorization',
        'auth_complete_message': 'Close Edge after signing in to YouTube, then click OK.',
        'edge_launched': 'Edge launched for authorization. Close it after signing in.',
        
        'profile_locked_title': 'Profile Locked',
        'profile_locked_message': (
            'Please close Edge authorization window before starting, '
            'as the browser locks access to data.'
        ),
        'close_edge_retry': 'Close Edge and try again',
        
        'no_format_selected': 'No format selected.',
        'analyze_first': 'Analyze URL first.',
        'enter_url': 'Enter video URL',
        
        # Convert tab
        'convert_title': '🔄 Offline Video Conversion',
        'select_file_group': '1. Select File',
        'input_file_not_selected': 'Input file: not selected',
        'select_video_file': 'Select video file...',
        
        'conversion_settings_group': '2. Conversion Settings',
        'video_codec': 'Video codec:',
        'audio_codec': 'Audio codec:',
        'quality_crf': 'Quality (CRF):',
        'audio_bitrate': 'Audio bitrate:',
        'container': 'Container:',
        
        'codec_h264': 'libx264 (H.264/AVC)',
        'codec_h265': 'libx265 (H.265/HEVC)',
        'codec_copy': 'copy (no re-encoding)',
        'codec_aac': 'aac (AAC)',
        'codec_mp3': 'libmp3lame (MP3)',
        
        'crf_excellent': '{} (excellent)',
        'crf_very_good': '{} (very good)',
        'crf_balanced': '{} (balanced)',
        'crf_acceptable': '{} (acceptable)',
        'crf_low': '{} (low)',
        
        'save_group': '3. Save',
        'output_file_auto': 'Output file: will be created automatically',
        'change_save_path': 'Change save path...',
        'start_conversion': '🚀 Start Conversion',
        
        'conversion_hints': (
            '💡 Tips:\n'
            '• CRF 18-20: high quality, large size\n'
            '• CRF 23: quality/size balance (recommended)\n'
            '• CRF 26-28: low quality, small size\n'
            "• 'copy' - copy without re-encoding (fast)"
        ),
        
        'input_file': 'Input file: {}',
        'output_file': 'Output file: {}',
        'select_input_first': 'Select input file first',
        'confirm_conversion_title': 'Confirmation',
        'confirm_conversion_message': 'Start conversion?\n\nInput file: {}\nOutput file: {}',
        'converting': 'Converting...',
        'conversion_complete': '✓ Conversion complete!',
        'conversion_error': '✗ Conversion error',
        'conversion_done_title': 'Done',
        'conversion_done_message': 'Conversion complete!\n\nFile saved:\n{}',
        'conversion_error_title': 'Conversion Error',
        'conversion_error_message': 'Failed to convert video:\n\n{}',
        
        # Placeholder
        'url_placeholder': 'Paste link to download video (youtube, ig, tiktok...)',
        
        # Update system
        'update_ytdlp': '🔄 Update yt-dlp',
        'update_ytdlp_text': 'Update yt-dlp',
        'update_tooltip_title': '💡 Tip',
        'update_tooltip_message': 'If something doesn\'t work, try updating yt-dlp using the button in the top right corner.',
        'updating_ytdlp': 'Updating yt-dlp...',
        'update_success': '✓ Updated to version {}',
        'update_not_needed': 'ℹ Already up to date (version {})',
        'update_error': '✗ Update error: {}',
        'update_complete_title': 'Update Complete',
        'update_error_title': 'Update Error',
    },
    
    'ru': {
        # Main window
        'app_name': 'Video extractor by ParallaXYZ',
        'analyze': 'Анализ',
        'auth_edge': 'Авторизация Edge',
        'change_folder': 'Изменить папку...',
        'folder': 'Папка',
        'ready': 'Готов',
        
        # Tabs
        'tab_download': '📥 Скачивание с YouTube',
        'tab_convert': '🔄 Конвертация видео',
        
        # Download tab
        'filter_all': 'Все',
        'filter_video': 'Видео',
        'filter_audio': 'Аудио',
        'filter_muxed': 'Совмещённые',
        'download_selected': 'Скачать выбранное',
        
        # Table headers
        'header_type': 'Тип',
        'header_container': 'Контейнер',
        'header_resolution': 'Разрешение/Битрейт',
        'header_fps': 'FPS',
        'header_size': 'Размер',
        'header_codecs': 'Кодеки',
        
        # Format types
        'type_video': 'видео',
        'type_audio': 'аудио',
        'type_muxed': 'совмещённое',
        
        # Messages
        'auth_required': '⚠ Требуется авторизация. Нажмите "Авторизация Edge".',
        'auth_detected': '✓ Авторизация обнаружена. Можно анализировать видео.',
        'analyzing': 'Анализ видео...',
        'formats_found': '✓ Найдено форматов: {}',
        'analysis_error': '✗ Ошибка анализа',
        'downloading': 'Скачивание...',
        'processing': 'Обработка...',
        'done': 'Готово',
        'saved_to': 'Готово. Сохранено в: {}',
        'error': 'Ошибка: {}',
        
        # Dialogs
        'auth_title': 'Авторизация в Edge',
        'auth_message': (
            'Сейчас откроется окно Microsoft Edge с изолированным профилем.\n\n'
            '1. Войдите в свой аккаунт YouTube\n'
            '2. Закройте окно Edge после входа\n'
            '3. Нажмите OK в этом окне после закрытия Edge\n\n'
            'ВАЖНО: Закройте Edge перед скачиванием!'
        ),
        'auth_complete_title': 'Завершение авторизации',
        'auth_complete_message': 'Закройте Edge после входа в аккаунт YouTube, затем нажмите OK.',
        'edge_launched': 'Edge запущен для авторизации. Закройте его после входа в аккаунт.',
        
        'profile_locked_title': 'Профиль заблокирован',
        'profile_locked_message': (
            'Пожалуйста, закройте окно авторизации Edge перед началом работы, '
            'так как браузер блокирует доступ к данным.'
        ),
        'close_edge_retry': 'Закройте Edge и попробуйте снова',
        
        'no_format_selected': 'Не выбран формат.',
        'analyze_first': 'Сначала анализируйте URL.',
        'enter_url': 'Введите URL видео',
        
        # Convert tab
        'convert_title': '🔄 Оффлайн конвертация видео',
        'select_file_group': '1. Выбор файла',
        'input_file_not_selected': 'Входной файл: не выбран',
        'select_video_file': 'Выбрать видео файл...',
        
        'conversion_settings_group': '2. Параметры конвертации',
        'video_codec': 'Видео кодек:',
        'audio_codec': 'Аудио кодек:',
        'quality_crf': 'Качество (CRF):',
        'audio_bitrate': 'Битрейт аудио:',
        'container': 'Контейнер:',
        
        'codec_h264': 'libx264 (H.264/AVC)',
        'codec_h265': 'libx265 (H.265/HEVC)',
        'codec_copy': 'copy (без перекодирования)',
        'codec_aac': 'aac (AAC)',
        'codec_mp3': 'libmp3lame (MP3)',
        
        'crf_excellent': '{} (отличное)',
        'crf_very_good': '{} (очень хорошее)',
        'crf_balanced': '{} (баланс)',
        'crf_acceptable': '{} (приемлемое)',
        'crf_low': '{} (низкое)',
        
        'save_group': '3. Сохранение',
        'output_file_auto': 'Выходной файл: будет создан автоматически',
        'change_save_path': 'Изменить путь сохранения...',
        'start_conversion': '🚀 Начать конвертацию',
        
        'conversion_hints': (
            '💡 Подсказки:\n'
            '• CRF 18-20: высокое качество, большой размер\n'
            '• CRF 23: баланс качества и размера (рекомендуется)\n'
            '• CRF 26-28: низкое качество, маленький размер\n'
            '• \'copy\' - копирование без перекодирования (быстро)'
        ),
        
        'input_file': 'Входной файл: {}',
        'output_file': 'Выходной файл: {}',
        'select_input_first': 'Сначала выберите входной файл',
        'confirm_conversion_title': 'Подтверждение',
        'confirm_conversion_message': 'Начать конвертацию?\n\nВходной файл: {}\nВыходной файл: {}',
        'converting': 'Конвертация...',
        'conversion_complete': '✓ Конвертация завершена успешно!',
        'conversion_error': '✗ Ошибка конвертации',
        'conversion_done_title': 'Готово',
        'conversion_done_message': 'Конвертация завершена!\n\nФайл сохранён:\n{}',
        'conversion_error_title': 'Ошибка конвертации',
        'conversion_error_message': 'Не удалось конвертировать видео:\n\n{}',
        
        # Placeholder
        'url_placeholder': 'Вставьте ссылку для скачивания видео (youtube, ig, tiktok...)',
        
        # Update system
        'update_ytdlp': '🔄 Обновить yt-dlp',
        'update_ytdlp_text': 'Обновить yt-dlp',
        'update_tooltip_title': '💡 Подсказка',
        'update_tooltip_message': 'Если что-то не работает, попробуйте обновить yt-dlp с помощью кнопки в правом верхнем углу.',
        'updating_ytdlp': 'Обновление yt-dlp...',
        'update_success': '✓ Обновлено до версии {}',
        'update_not_needed': 'ℹ Уже актуальная версия ({})',
        'update_error': '✗ Ошибка обновления: {}',
        'update_complete_title': 'Обновление завершено',
        'update_error_title': 'Ошибка обновления',
    }
}


class Translator:
    """Simple translator class"""
    
    def __init__(self, language='en'):
        self.language = language
    
    def set_language(self, language):
        """Change current language"""
        if language in TRANSLATIONS:
            self.language = language
    
    def tr(self, key):
        """Translate key to current language"""
        return TRANSLATIONS.get(self.language, {}).get(key, key)
    
    def get_language(self):
        """Get current language"""
        return self.language


# Global translator instance
translator = Translator('ru')  # Default to Russian
