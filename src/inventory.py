"""Progreso del jugador dentro de la partida."""
from . import settings as S


class Progress:
    def __init__(self):
        self.hearts = S.MAX_HEARTS
        self.flowers = 0
        self.total_flowers = 0
        self.ammo = 0
        self.power = False
        self.level_index = 0
        self.unlocked = 1
        self.hero = "flora"
        self.target = "dama"
        self.deaths = 0

    def reset_level(self):
        self.hearts = S.MAX_HEARTS
        self.flowers = 0
        if self.power:
            self.ammo = S.MAX_AMMO

    def unlock_power(self):
        self.power = True
        self.ammo = S.MAX_AMMO

    def add_ammo(self, n=S.MAX_AMMO):
        self.ammo = min(S.MAX_AMMO, self.ammo + n)

    def to_dict(self):
        return {
            "personaje": self.hero, "destinatario": self.target,
            "nivel_actual": self.level_index, "nivel_desbloqueado": self.unlocked,
            "flores_totales": self.total_flowers, "poder": self.power,
            "muertes": self.deaths,
        }

    def from_dict(self, d):
        self.hero = d.get("personaje", "flora")
        self.target = d.get("destinatario", "dama")
        self.level_index = int(d.get("nivel_actual", 0))
        self.unlocked = int(d.get("nivel_desbloqueado", 1))
        self.total_flowers = int(d.get("flores_totales", 0))
        self.power = bool(d.get("poder", False))
        self.deaths = int(d.get("muertes", 0))
        if self.power:
            self.ammo = S.MAX_AMMO
