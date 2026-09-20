import os
import time
import numpy as np
import pygame
import soundfile as sf

SRC = os.path.join("assets", "music", "flores amarillas (online-audio-converter.com).mp3")
DST = os.path.join("assets", "music", "flores_amarillas_final.ogg")
if os.path.exists(DST):
    os.remove(DST)

t0 = time.time()
pygame.mixer.quit()
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init(44100, -16, 2, 512)
snd = pygame.mixer.Sound(SRC)
arr = pygame.sndarray.array(snd)
if arr.dtype != np.int16:
    arr = arr.astype(np.int16)
print("mp3 decodificado:", arr.shape, arr.dtype, "dur=%.1fs" % (len(arr) / 44100.0),
      "tiempo=%.1fs" % (time.time() - t0))

a = arr.astype(np.float32) / 32768.0
if a.ndim == 1:
    a = np.column_stack([a, a])
print("canales:", a.shape)
sf.write(DST, a, 44100, format="OGG", subtype="VORBIS")
print("OGG ESCRITO:", DST, "%.2f MB" % (os.path.getsize(DST) / 1e6),
      "dur=%.1fs" % (len(a) / 44100.0), "tiempo=%.1fs" % (time.time() - t0))
