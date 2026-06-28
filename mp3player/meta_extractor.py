import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1
from PyQt6.QtGui import QPixmap, QImage

def get_metadata(file_path):
    metadata = {"title": os.path.basename(file_path), "artist": "Unknown", "cover": None}
    if not os.path.exists(file_path):
        return metadata
    try:
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
    except Exception:
        pass
    return metadata

