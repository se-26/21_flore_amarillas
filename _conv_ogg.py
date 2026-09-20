import os, numpy as np
import pygame

SRC = r"assets\music\flores amarillas (online-audio-converter.com).mp3"
DST = r"assets\music\flores_amarillas_final.ogg"
if os.path.exists(DST): os.remove(DST)

pygame.mixer.quit(); pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init(44100, -16, 2, 512)
snd = pygame.mixer.Sound(SRC)
arr = pygame.sndarray.array(snd)
print("formato:", arr.dtype, arr.shape, "dur=%.1fs" % (len(arr)/44100.0))
arrf = arr.astype(np.float32) / 32768.0
if arrf.ndim == 1:
    arrf = np.column_stack([arrf, arrf])

import soundfile as sf
sf.write(DST, arrf, 44100, format="OGG", subtype="VORBIS")
print("OGG escrito:", round(os.path.getsize(DST)/1024/1024,2), "MB")
