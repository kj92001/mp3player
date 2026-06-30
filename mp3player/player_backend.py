import os
import sys
import ctypes  # 💡 1. ctype에서 ctypes로 오타 수정
from PySide6.QtCore import QObject, Signal, QTimer

# 💡 2. 우분투 24.04 환경 맞춤 VLC 라이브러리 및 플러그인 경로 강제 지정
sys_vlc_core = '/usr/lib/x86_64-linux-gnu/libvlccore.so.9'
sys_vlc_lib = '/usr/lib/x86_64-linux-gnu/libvlc.so.5'
sys_vlc_plugins = '/usr/lib/x86_64-linux-gnu/vlc/plugins'

# 우분투 시스템 마이너 버전에 따라 .so.9가 없을 경우 .so.8 등으로 자동 탐색 유연화
if not os.path.exists(sys_vlc_core):
    sys_vlc_core = '/usr/lib/x86_64-linux-gnu/libvlccore.so.8'

try:
    if os.path.exists(sys_vlc_core) and os.path.exists(sys_vlc_lib):
        # ctypes를 사용하여 시스템 메모리에 VLC 핵심 엔진 바이너리를 선제 고정
        ctypes.CDLL(sys_vlc_core)
        ctypes.CDLL(sys_vlc_lib)
        # 단일 실행 파일 내에서 오디오/비디오 코덱 플러그인을 찾을 수 있게 환경 변수 주입
        os.environ['VLC_PLUGIN_PATH'] = sys_vlc_plugins
except Exception as e:
    print(f"⚠️ 우분투 시스템 VLC 엔진 프리로드 경고: {e}")

# 💡 3. 모든 경로 바인딩 작전이 끝난 직후 vlc를 안전하게 임포트합니다.
import vlc

class PlayerBackend(QObject):
    position_changed = Signal(int)
    duration_changed = Signal(int)
    media_finished = Signal()

    def __init__(self):
        super().__init__()
        
        # 상단에서 메모리에 띄워둔 물리 바이너리 덕분에 NoneType 에러 없이 객체가 생성됩니다.
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
        # 최대 볼륨을 115로 제한합니다.
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

