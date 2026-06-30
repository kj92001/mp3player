import sys
import os

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    if sys._MEIPASS not in sys.path:
        sys.path.insert(0, sys._MEIPASS)
    os.chdir(sys._MEIPASS)

from PySide6.QtWidgets import QMainWindow, QApplication, QListWidgetItem, QMessageBox, QFileDialog
from PySide6.QtCore import Qt
# from PySide6.QtUiTools import QUiLoader  #  PySide6 전용 UI 로더
# from PySide6.QtCore import QFile  
import config
from meta_extractor import get_metadata
from player_backend import PlayerBackend
from mp3player_ui import Ui_MainWindow

class MP3PlayerApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        
        try:
            self.setupUi(self)
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
        self.btnStop.clicked.connect(self.pause_music)    # 🛠️ 기존 정지 버튼을 일시정지 함수에 연결
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

        self.load_saved_data()

    def play_music(self):
        """곡을 새로 재생하거나 일시정지 상태에서 이어서 재생합니다."""
        if self.playlist_paths:
            if self.current_index == -1:
                self.current_index = 0
                self.play_current()
            else:
                self.backend.play()

    # 🛠️ 기존 정지 대신 작동할 일시정지 함수
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

    def move_down(self):
        row = self.listWidget.currentRow()
        if row < self.listWidget.count() - 1 and row != -1:
            item = self.listWidget.takeItem(row)
            self.listWidget.insertItem(row + 1, item)
            self.playlist_paths.insert(row + 1, self.playlist_paths.pop(row))
            self.listWidget.setCurrentRow(row + 1)

    def delete_item(self):
        row = self.listWidget.currentRow()
        if row != -1:
            self.listWidget.takeItem(row)
            self.playlist_paths.pop(row)
            if self.current_index == row: 
                self.backend.stop()
                self.current_index = -1

    def open_directory_dialog(self):
        selected_dir = QFileDialog.getExistingDirectory(
            self, 
            "음악 파일이 있는 폴더 선택", 
            os.path.expanduser("~")
        )
        if selected_dir:
            mp3_found = False
            for filename in os.listdir(selected_dir):
                if filename.lower().endswith('.mp3'):
                    full_path = os.path.join(selected_dir, filename)
                    self.add_mp3_to_list(full_path)
                    mp3_found = True
            
            if not mp3_found:
                QMessageBox.information(self, "안내", "선택한 폴더 안에 MP3 파일이 존재하지 않습니다.")

    def handle_scrollbar_dynamic(self, min_val, max_val):
        self.verticalScrollBar.setRange(min_val, max_val)
        self.verticalScrollBar.setVisible(max_val > 0)

    def load_saved_data(self):
        try:
            data = config.load_settings()
            geo = data.get("window_geometry")
            if geo and len(geo) == 4: 
                self.setGeometry(geo[0], geo[1], geo[2], geo[3])
            
            playlist = data.get("playlist", [])
            for path in playlist:
                if os.path.exists(path): 
                    self.add_mp3_to_list(path)
                    
            vol = data.get("volume", 50)
            self.sliderVolume.setValue(vol)
            self.backend.set_volume(vol)
        except Exception as e:
            print(f"⚠️ 설정 로드 실패: {e}")

    def closeEvent(self, event):
        try:
            geom = self.geometry()
            config.save_settings(self.playlist_paths, self.current_index, self.sliderVolume.value(), [geom.x(), geom.y(), geom.width(), geom.height()])
        except Exception as e:
            print(f"⚠️ 설정 저장 실패: {e}")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MP3PlayerApp()
    player.show()
    sys.exit(app.exec())

