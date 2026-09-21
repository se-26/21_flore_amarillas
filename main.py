"""21 de Septiembre: Flores para Ti.

Punto de entrada. Ejecuta:  python main.py
(tambien compatible con exportacion web via pygbag)
"""
import asyncio

import pygame

from src.game import Game


async def main():
    game = Game()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())