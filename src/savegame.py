"""Guardado y configuracion en JSON, a prueba de archivos corruptos."""
import json
import os

from . import settings as S

DEFAULT = {
    "personaje": "flora",
    "destinatario": "dama",
    "nivel_actual": 0,
    "nivel_desbloqueado": 1,
    "flores_totales": 0,
    "poder": False,
    "muertes": 0,
    "audio": {"musica": True, "efectos": True,
              "volumen_musica": 0.45, "volumen_efectos": 0.6},
}


def load():
    """Devuelve siempre un diccionario valido; repara el archivo si hace falta."""
    if not os.path.isfile(S.SAVE_PATH):
        save(DEFAULT)
        return dict(DEFAULT)
    try:
        with open(S.SAVE_PATH, encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            raise ValueError("formato invalido")
    except (OSError, ValueError):
        save(DEFAULT)
        return dict(DEFAULT)
    merged = dict(DEFAULT)
    merged.update({k: v for k, v in data.items() if k in DEFAULT})
    audio = dict(DEFAULT["audio"])
    if isinstance(data.get("audio"), dict):
        audio.update(data["audio"])
    merged["audio"] = audio
    return merged


def save(data):
    try:
        with open(S.SAVE_PATH, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def has_progress():
    d = load()
    return d.get("nivel_desbloqueado", 1) > 1 or d.get("nivel_actual", 0) > 0
