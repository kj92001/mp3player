import sys
import os
import json  # 설정 파일 파싱을 위해 추가

# 1. Linux 환경 VLC 플러그인 경로 설정 (최상단 배치)
if getattr(sys, 'frozen', False) or sys.platform.startswith('linux'):
    os.environ['PYTHON_VLC_MODULE_PATH'] = '/usr/lib/x86_64-linux-gnu/vlc/plugins'

from PyQt6.QtWidgets import QMainWindow, QApplication, QListWidgetItem, QMessageBox, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.uic import loadUi

import config
from meta_extractor import get_metadata
from player_backend import PlayerBackend


# 2. PyInstaller 임시 폴더 경로 추적 함수
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class MP3PlayerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # UI 파일 로드
        ui_path = resource_path("mp3player.ui")
        try:
            loadUi(ui_path, self)
        except Exception as e:
            print(f"❌ UI 파일 로드 실패: {e}")
            sys.exit(1)
        
        self.backend = PlayerBackend()
        self.playlist_paths = []
        self.current_index = -1

        self.sliderVolume.setMaximum(115)

        # 드래그 앤 드롭 설정
        self.setAcceptDrops(True)
        self.listWidget.setAcceptDrops(True)
        self.listWidget.setDragDropMode(self.listWidget.DragDropMode.InternalMove)

        # 시그널 연결
        self.btnPlay.clicked.connect(self.play_music)
        self.btnStop.clicked.connect(self.pause_music)    
        self.btnNext.clicked.connect(self.play_next)
        self.btnPrev.clicked.connect(self.play_prev)
        self.btnUp.clicked.connect(self.move_up)
        self.btnDown.clicked.connect(self.move_down)
        self.btnDelete.clicked.connect(self.delete_item)
        
        try:
            self.btnOpenDir.clicked.connect(self.open_directory_dialog)
        except AttributeError:
            print("❌ 오류: UI 파일에 'btnOpenDir' 오브젝트 이름이 없습니다.")

        self.sliderVolume.valueChanged.connect(self.backend.set_volume)
        self.sliderProgress.sliderMoved.connect(self.backend.set_position)
        
        self.backend.position_changed.connect(self.update_position)
        self.backend.duration_changed.connect(self.update_duration)
        self.backend.media_finished.connect(self.play_next)
        
        self.listWidget.itemDoubleClicked.connect(self.item_double_clicked)
        self.listWidget.itemActivated.connect(self.item_double_clicked)
        self.listWidget.model().rowsMoved.connect(self.sync_playlist_order)

        # 스크롤바 설정
        self.listWidget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.verticalScrollBar.hide()
        self.listWidget.verticalScrollBar().valueChanged.connect(self.verticalScrollBar.setValue)
        self.verticalScrollBar.valueChanged.connect(self.listWidget.verticalScrollBar().setValue)
        self.listWidget.verticalScrollBar().rangeChanged.connect(self.handle_scrollbar_dynamic)

        # ⭐ [수정] 프로그램 시작 시 저장된 재생 목록을 확실하게 로드합니다.
        self.load_saved_data()

    def play_music(self):
        """곡을 새로 재생하거나 일시정지 상태에서 이어서 재생합니다."""
        if self.playlist_paths:
            if self.current_index == -1:
                self.current_index = 0
                self.play_current()
            else:
                self.backend.play()

    def pause_music(self):
        """곡이 재생 중일 때 그 자리에 일시정지합니다."""
        if self.backend.player.is_playing():
            self.backend.pause()

    def play_current(self):
        if 0 <= self.current_index < len(self.playlist_paths):
            self.listWidget.setCurrentRow(self.current_index)
            path = self.playlist_paths[self.current_index]
            self.backend.play_file(path)
            
            meta = get_metadata(path)
            self.lblTitle.setText(f"제목: {meta.get('title', 'Unknown')}")
            self.lblArtist.setText(f"가수: {meta.get('artist', 'Unknown')}")
            
            if meta.get('cover'):
                self.lblCover.setPixmap(meta['cover'].scaled(350, 350, Qt.AspectRatioMode.KeepAspectRatio))
            else:
                self.lblCover.setText("No Image")

    def update_position(self, pos):
        self.sliderProgress.setValue(pos)
        self.update_time_label(pos, self.backend.player.get_length())

    def update_duration(self, dur):
        self.sliderProgress.setMaximum(dur)

    def update_time_label(self, pos, dur):
        pm, ps = divmod(pos // 1000, 60)
        dm, ds = divmod(dur // 1000, 60)
        self.lblTime.setText(f"{pm:02d}:{ps:02d} / {dm:02d}:{ds:02d}")

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        current_volume = self.sliderVolume.value()
        step = 5
        new_volume = min(max(current_volume + (step if delta > 0 else -step), 0), 110)
        self.sliderVolume.setValue(new_volume)

    def add_mp3_to_list(self, path):
        path = os.path.abspath(os.path.normpath(path))
        if path not in self.playlist_paths:
            self.playlist_paths.append(path)
            item = QListWidgetItem(os.path.basename(path))
            item.setData(Qt.ItemDataRole.UserRole, path)
            self.listWidget.addItem(item)
            # 곡이 추가될 때마다 세이브 파일에 자동 저장 유도
            self.save_current_data()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith('.mp3'):
                    self.add_mp3_to_list(file_path)
            event.acceptProposedAction()

    def sync_playlist_order(self, parent, start, end, destination, row):
        new_paths = []
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            if item:
                new_paths.append(item.data(Qt.ItemDataRole.UserRole))
        self.playlist_paths = new_paths
        self.save_current_data()

    def play_next(self):
        if self.playlist_paths:
            self.current_index = (self.current_index + 1) % len(self.playlist_paths)
            self.play_current()

    def play_prev(self):
        if self.playlist_paths:
            self.current_index = (self.current_index - 1) % len(self.playlist_paths)
            self.play_current()

    def item_double_clicked(self, item):
        self.current_index = self.listWidget.row(item)
        self.play_current()

    def move_up(self):
        row = self.listWidget.currentRow()
        if row > 0:
            item = self.listWidget.takeItem(row)
            self.listWidget.insertItem(row - 1, item)
            self.playlist_paths.insert(row - 1, self.playlist_paths.pop(row))
            self.listWidget.setCurrentRow(row - 1)
            self.save_current_data()

    def move_down(self):
        row = self.listWidget.currentRow()
        if row < self.listWidget.count() - 1 and row != -1:
            item = self.listWidget.takeItem(row)
            self.listWidget.insertItem(row + 1, item)
            self.playlist_paths.insert(row + 1, self.playlist_paths.pop(row))
            self.listWidget.setCurrentRow(row + 1)
            self.save_current_data()

    def delete_item(self):
        row = self.listWidget.currentRow()
        if row != -1:
            self.listWidget.takeItem(row)
            self.playlist_paths.pop(row)
            if self.current_index == row: 
                self.backend.stop()
                self.current_index = -1
            self.save_current_data()

    def handle_scrollbar_dynamic(self, min_val, max_val):
        self.verticalScrollBar.setRange(min_val, max_val)
        if max_val > 0:
            self.verticalScrollBar.show()
        else:
            self.verticalScrollBar.hide()

    def open_directory_dialog(self):
        dir_path = QFileDialog.getExistingDirectory(self, "폴더 열기", os.path.expanduser("~"))
        if dir_path:
            for root, dirs, files in os.walk(dir_path):
                for file in sorted(files):
                    if file.lower().endswith('.mp3'):
                        full_path = os.path.join(root, file)
                        self.add_mp3_to_list(full_path)

    # ⭐ [기능 복구] json 파일 등에서 재생목록을 복원하는 핵심 로직
    def load_saved_data(self):
        config_path = resource_path("player_config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # json 구조에 따라 'playlist' 혹은 저장되어 있던 키값을 매핑합니다.
                    saved_paths = data.get("playlist", [])
                    for path in saved_paths:
                        if os.path.exists(path):
                            self.add_mp3_to_list(path)
            except Exception as e:
                print(f"⚠️ 설정 로드 실패: {e}")

    # ⭐ [기능 추가] 목록 변동 시 세이브 데이터를 갱신하는 보조 로직
    def save_current_data(self):
        config_path = resource_path("player_config.json")
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump({"playlist": self.playlist_paths}, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"⚠️ 설정 저장 실패: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MP3PlayerApp()
    player.show()
    sys.exit(app.exec())

