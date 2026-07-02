import os
import sys
import ctypes  
from PySide6.QtCore import QObject, Signal, QTimer

# [VLC 라이브러리 및 플러그인 경로 강제 지정 구문]
sys_vlc_core = '/usr/lib/x86_64-linux-gnu/libvlccore.so.9'
sys_vlc_lib = '/usr/lib/x86_64-linux-gnu/libvlc.so.5'
sys_vlc_plugins = '/usr/lib/x86_64-linux-gnu/vlc/plugins'

if not os.path.exists(sys_vlc_core):
    sys_vlc_core = '/usr/lib/x86_64-linux-gnu/libvlccore.so.8'

try:
    if os.path.exists(sys_vlc_core) and os.path.exists(sys_vlc_lib):
        ctypes.CDLL(sys_vlc_core)
        ctypes.CDLL(sys_vlc_lib)
        os.environ['VLC_PLUGIN_PATH'] = sys_vlc_plugins
except Exception as e:
    print(f"⚠️ 우분투 시스템 VLC 엔진 프리로드 경고: {e}")

import vlc

class PlayerBackend(QObject):
    position_changed = Signal(int)
    duration_changed = Signal(int)

    def __init__(self):
        super().__init__()
        
        # 🛠️ quiet 옵션으로 앨범아트 파싱 에러(mjpeg demux) 등의 잔여 로그 출력을 차단합니다.
        self.instance = vlc.Instance('--quiet', '--no-video')
        self.player = self.instance.media_player_new()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_ui)
        self.timer.setInterval(300)

    def play_file(self, file_path):
        if os.path.exists(file_path):
            self.stop()
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
        self.timer.stop()
        self.player.stop()
        self.player.set_media(None)
        
    def destroy(self):
        """VLC 플레이어와 인스턴스를 완전히 파괴하여 오디오 장치 점유를 해제합니다."""
        try:
            self.timer.stop()
            if self.player:
                self.player.stop()
                self.player.release()
            if self.instance:
                self.instance.release()
        except Exception as e:
            print(f"정리 중 예외 무시: {e}")

    def set_volume(self, value):
        safe_volume = min(value, 110)
        if self.player:
            self.player.audio_set_volume(safe_volume)
        
    def set_position(self, position):
        if self.player:
            self.player.set_time(position)

    def _update_ui(self):
        if self.player and self.player.is_playing():
            time_ms = self.player.get_time()
            length_ms = self.player.get_length()
            
            if time_ms >= 0:
                self.position_changed.emit(time_ms)
            if length_ms > 0:
                self.duration_changed.emit(length_ms)
