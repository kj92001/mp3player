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
    media_finished = Signal()

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
        safe_volume = min(value, 110)
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

    # 💡 [수정] VLC 자체 스레드에서 직접 Signal을 쏘지 않도록 변경
    def _on_media_finished(self, event):
        # QTimer.singleShot(0, ...)을 사용해 Qt의 메인 GUI 스레드로 작업을 토스합니다.
        # 이렇게 해야 리눅스 환경에서 프로그램이 갑자기 꺼지는(Crash) 현상을 막을 수 있습니다.
        QTimer.singleShot(0, self._handle_media_finished_safe)

    # 💡 [추가] Qt 메인 스레드에서 안전하게 실행될 콜백 함수
    def _handle_media_finished_safe(self):
        self.timer.stop()          # 재생이 끝났으므로 UI 갱신 타이머를 멈춥니다.
        self.media_finished.emit() # 안전하게 종료 시그널을 발생시킵니다.

