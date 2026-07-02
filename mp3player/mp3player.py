import sys
import os

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    if sys._MEIPASS not in sys.path:
        sys.path.insert(0, sys._MEIPASS)
    os.chdir(sys._MEIPASS)

from PySide6.QtWidgets import QMainWindow, QApplication, QListWidgetItem, QMessageBox, QFileDialog
from PySide6.QtCore import Qt, QTimer
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
        
        self.backend = None
        self.playlist_paths = []
        self.current_index = -1
        self.is_transitioning = False 

        # 초기 백엔드 생성 및 연결
        self.recreate_backend()

        self.sliderVolume.setMaximum(115)

        # 드래그 앤 드롭 설정
        self.setAcceptDrops(True)
        self.listWidget.setAcceptDrops(True)
        self.listWidget.setDragDropMode(self.listWidget.DragDropMode.InternalMove)

        # 시그널 연결
        self.btnPlay.clicked.connect(self.play_music)
        self.btnStop.clicked.connect(self.stop_music)
        self.btnPause.clicked.connect(self.pause_music)    
        self.btnNext.clicked.connect(self.play_next)
        self.btnPrev.clicked.connect(self.play_prev)
        self.btnDelete.clicked.connect(self.delete_item)
        self.btnFullDelete.clicked.connect(self.fullDelete_item)
        
        try:
            self.btnOpenDir.clicked.connect(self.open_directory_dialog)
        except AttributeError:
            print("❌ 오류: UI 파일에 'btnOpenDir' 오브젝트 이름이 없습니다.")

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

    def recreate_backend(self):
        """🛠️ 기존 백엔드를 메모리에서 완전히 소멸시키고 새로 깨끗하게 생성합니다."""
        if self.backend is not None:
            try:
                self.backend.position_changed.disconnect()
                self.backend.duration_changed.disconnect()
                self.backend.destroy()
            except:
                pass
        
        # 기존 백엔드가 물고 있던 타겟 슬라이더 메서드를 안전하게 연결 해제
        if self.backend is not None:
            try:
                self.sliderVolume.valueChanged.disconnect(self.backend.set_volume)
            except (TypeError, RuntimeError):
                pass
            try:
                self.sliderProgress.sliderMoved.disconnect(self.backend.set_position)
            except (TypeError, RuntimeError):
                pass

        self.backend = PlayerBackend()
        self.backend.position_changed.connect(self.update_position)
        self.backend.duration_changed.connect(self.update_duration)
        
        self.sliderVolume.valueChanged.connect(self.backend.set_volume)
        self.sliderProgress.sliderMoved.connect(self.backend.set_position)
        
        # 현재 화면에 세팅된 볼륨값 백엔드에 즉시 주입
        self.backend.set_volume(self.sliderVolume.value())

    def play_music(self):
        if self.playlist_paths:
            if self.current_index == -1:
                self.current_index = 0
            self.play_current()

    def stop_music(self):
        if self.backend:
            self.backend.stop()

    def pause_music(self):
        if self.backend:
            self.backend.pause()

    def play_current(self):
        if 0 <= self.current_index < len(self.playlist_paths):
            self.listWidget.setCurrentRow(self.current_index)
            path = self.playlist_paths[self.current_index]
            
            # 새 곡 재생 직전 무조건 백엔드를 새로고침하여 에러 원천 차단
            self.recreate_backend()
            
            self.backend.play_file(path)
            self.is_transitioning = False  
            
            meta = get_metadata(path)
            self.lblTitle.setText(f"제목: {meta.get('title', 'Unknown')}")
            self.lblArtist.setText(f"가수: {meta.get('artist', 'Unknown')}")
            
            if meta.get('cover'):
                self.lblCover.setPixmap(meta['cover'].scaled(350, 350, Qt.AspectRatioMode.KeepAspectRatio))
            else:
                self.lblCover.setText("이미지 없음")
                self.lblCover.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def update_position(self, pos):
        self.sliderProgress.setValue(pos)
        if self.backend and self.backend.player:
            dur = self.backend.player.get_length()
            self.update_time_label(pos, dur)
            
            # 남은 시간이 500ms 이하가 되면 다음 곡으로 토스
            if dur > 0 and (dur - pos) <= 500:
                if not self.is_transitioning:
                    self.is_transitioning = True
                    QTimer.singleShot(50, self.auto_play_next)

    def update_duration(self, dur):
        self.sliderProgress.setMaximum(dur)

    def update_time_label(self, pos, dur):
        pm, ps = divmod(pos // 1000, 60)
        dm, ds = divmod(dur // 1000, 60)
        self.lblTime.setText(f"{pm:02d}:{ps:02d} / {dm:02d}:{ds:02d}")

    def eventFilter(self, obj, event):
        from PySide6.QtCore import QEvent
        if obj == self.sliderVolume and event.type() == QEvent.Type.Wheel:
            delta = event.angleDelta().y()
            current_volume = self.sliderVolume.value()
            step = 5
            new_volume = min(max(current_volume + (step if delta > 0 else -step), 0), 110)
            self.sliderVolume.setValue(new_volume)
            return True  
        return super().eventFilter(obj, event)

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
                if file_path.lower().endswith(('.mp3','flac')):
                    self.add_mp3_to_list(file_path)
            event.acceptProposedAction()

    def sync_playlist_order(self, parent, start, end, destination, row):
        new_paths = []
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            if item:
                new_paths.append(item.data(Qt.ItemDataRole.UserRole))
        self.playlist_paths = new_paths

    def auto_play_next(self):
        if not self.playlist_paths:
            return
        self.current_index = (self.current_index + 1) % len(self.playlist_paths)
        self.play_current()

    def play_next(self):
        if not self.playlist_paths:
            return
        self.current_index = (self.current_index + 1) % len(self.playlist_paths)
        self.play_current()

    def play_prev(self):
        if self.playlist_paths:
            self.current_index = (self.current_index - 1) % len(self.playlist_paths)
            self.play_current()

    def item_double_clicked(self, item):
        self.current_index = self.listWidget.row(item)
        self.play_current()

    def delete_item(self):
        row = self.listWidget.currentRow()
        if row != -1:
            self.listWidget.takeItem(row)
            self.playlist_paths.pop(row)
            if self.current_index == row: 
                if self.backend: self.backend.stop()
                self.current_index = -1
            elif self.current_index > row:
                self.current_index -= 1

    def fullDelete_item(self):
        if self.backend: self.backend.stop()
        self.current_index = -1
        self.listWidget.clear()
        self.playlist_paths.clear()  

    def open_directory_dialog(self):
        selected_dir = QFileDialog.getExistingDirectory(
            self, 
            "음악 파일이 있는 폴더 선택", 
            os.path.expanduser("~")
        )
        if selected_dir:
            mp3_found = False
            for filename in os.listdir(selected_dir):
                if filename.lower().endswith(('.mp3','flac')):
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
            if self.backend: self.backend.set_volume(vol)
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
