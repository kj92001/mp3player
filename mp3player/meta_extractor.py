import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1
from mutagen.flac import FLAC
from PySide6.QtGui import QPixmap, QImage

def get_metadata(file_path):
    metadata = {"title": os.path.basename(file_path), "artist": "Unknown", "cover": None}
    if not os.path.exists(file_path):
        return metadata
        
    # 💡 [추가] 누락되었던 확장자 추출 변수를 명확히 정의합니다.
    file_ext = os.path.splitext(file_path)[1].lower()
    
    try:
        # 💡 [구조 변경] 파일 확장자에 따라 MP3와 FLAC 엔진을 완전히 분리해서 실행해야 합니다.
        if file_ext == '.mp3':
            audio = MP3(file_path, ID3=ID3)
            if audio.tags:
                if 'TPE1' in audio.tags:
                    metadata["artist"] = audio.tags['TPE1'].text[0]
                if 'TIT2' in audio.tags:
                    metadata["title"] = audio.tags['TIT2'].text[0]
                
                for key in audio.tags.keys():
                    if key.startswith('APIC'):
                        apic = audio.tags[key]
                        img_data = apic.data
                        image = QImage.fromData(img_data)
                        metadata["cover"] = QPixmap.fromImage(image)
                        break
                        
        elif file_ext == '.flac':
            audio = FLAC(file_path)

            if 'artist' in audio:
                metadata["artist"] = audio['artist'][0]
            if 'title' in audio:
                metadata["title"] = audio['title'][0]

            # 💡 작성해주신 아래의 FLAC 앨범아트 추출 로직([0] 번방 접근)은 완벽합니다!
            if audio.pictures:
                img_data = audio.pictures[0].data
                image = QImage.fromData(img_data)
                metadata["cover"] = QPixmap.fromImage(image)

    except Exception as e:
        # 주석을 해제하시면 혹시 모를 내부 에러를 터미널에서 확인할 수 있습니다.
        # print(f"메타데이터 추출에러 ({file_ext}): {e}")
        pass
        
    return metadata

