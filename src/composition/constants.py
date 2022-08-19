from enum import Enum
from typing import Dict, Any


class EntityDataKey(str, Enum):
    HEALTH = "health"
    ATTACK = "attack"
    DRAWING_LAYERS = "drawing_layers"
    POSITION = "position"


class Sprite(str, Enum):
    PLAYER = "┌( ಠ_ಠ)┘"
    BEAR = " ʕಠಿᴥಠʔ "
    SWORD = "--o::::>"
    LANCE = "------->"
    TERRAIN = "XXXXXXXX"


class Effect(str, Enum):
    FIRE = "*"
    WET = "o"
    SMOKED = "#"


Input = str
EntityData = Dict[EntityDataKey, Any]
