import os
import vlc
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

class PlayerBackend(QObject):
    position_changed = pyqtSignal(int)
    duration_changed = pyqtSignal(int)
    media_finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        
        self.events = self.player.event_manager()
        self.events.event_attach(vlc.EventType.MediaPlayerEndReached, self._on_media_finished)

        self.timer = QTimer()
        self.timer.timeout.connect(self._update_ui)
        self.timer.setInterval(500)

    def play_file(self, file_path):
        if os.path.exists(file_path):
            media = self.instance.media_new(file_path)
            self.player.set_media(media)
            self.player.play()
            self.timer.start()

    def play(self): 
        self.player.play()
        self.timer.start()

    def pause(self): 
        self.player.pause()
        self.timer.stop()

    def stop(self): 
        self.player.stop()
        self.timer.stop()
        
    def set_volume(self, value):
        # 최대 볼륨을 124로 제한합니다.
        safe_volume = min(value, 115)
        self.player.audio_set_volume(safe_volume)
        
    def set_position(self, position):
        self.player.set_time(position)

    def _update_ui(self):
        if self.player.is_playing():
            time = self.player.get_time()
            length = self.player.get_length()
            
            if time >= 0:
                self.position_changed.emit(time)
            if length > 0:
                self.duration_changed.emit(length)

    def _on_media_finished(self, event):
        self.media_finished.emit()
