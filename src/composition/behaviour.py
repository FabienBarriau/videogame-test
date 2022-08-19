from __future__ import annotations
from typing import Dict, Optional
from abc import ABC, abstractmethod
from composition.constants import EntityDataKey, Input, Effect


class Behaviour(ABC):

    last: bool
    transitive: bool

    @abstractmethod
    def start(self, data: Dict):
        pass

    @abstractmethod
    def end(self, data: Dict):
        pass

    @abstractmethod
    def do(self, data: Dict, input: Input) -> Optional[Behaviour]:
        pass

    @abstractmethod
    def compose(self, other: Behaviour) -> Optional[Behaviour]:
        pass


class Drawable(Behaviour):
    def __init__(self, drawing: str):
        self.last = True
        self.transitive = False
        self.drawing = drawing

    def start(self, data: Dict):
        if EntityDataKey.DRAWING_LAYERS not in data:
            data[EntityDataKey.DRAWING_LAYERS] = [self.drawing]

    def end(self, data: Dict):
        pass

    def do(self, data: Dict, input: Input) -> Optional[Behaviour]:
        return Drawable(self.drawing)

    def compose(self, other: Behaviour) -> Optional[Behaviour]:
        return None


class Positioned(Behaviour):
    def __init__(self, init_position: int):
        self.last = False
        self.transitive = False
        self.init_position = init_position

    def start(self, data: Dict):
        if EntityDataKey.POSITION not in data:
            data[EntityDataKey.POSITION] = self.init_position

    def end(self, data: Dict):
        data.pop(EntityDataKey.POSITION)

    def do(self, data: Dict, input: Input) -> Optional[Behaviour]:
        return Positioned(self.init_position)

    def compose(self, other: Behaviour) -> Optional[Behaviour]:
        return None


class Alive(Behaviour):
    def __init__(self, init_health: int):
        self.last = True
        self.transitive = False
        self.init_health = init_health

    def start(self, data: Dict):
        if EntityDataKey.HEALTH not in data:
            data[EntityDataKey.HEALTH] = self.init_health

    def end(self, data: Dict):
        data.pop(EntityDataKey.HEALTH)

    def do(self, data: Dict, input: Input) -> Optional[Behaviour]:
        if data[EntityDataKey.HEALTH] <= 0:
            return Dead(self.init_health)
        else:
            return Alive(self.init_health)

    def compose(self, other: Behaviour) -> Optional[Behaviour]:
        return None


class Attacker(Behaviour):
    def __init__(self, init_attack: int):
        self.last = True
        self.transitive = False
        self.init_attack = init_attack

    def start(self, data: Dict):
        data[EntityDataKey.ATTACK] = self.init_attack

    def end(self, data: Dict):
        data.pop(EntityDataKey.ATTACK)

    def do(self, data: Dict, input: Input) -> Optional[Behaviour]:
        return Attacker(self.init_attack)

    def compose(self, other: Behaviour) -> Optional[Behaviour]:
        return None


class Dead(Behaviour):
    def __init__(self, init_health: int):
        self.last = True
        self.transitive = False
        self.init_health = init_health

    def start(self, data: Dict):
        pass

    def end(self, data: Dict):
        pass

    def do(self, data: Dict, input: Input) -> Optional[Behaviour]:
        return None

    def compose(self, other: Behaviour) -> Optional[Behaviour]:
        return None


class Smoked(Behaviour):
    def __init__(self, duration: int, effect_draw: Optional[str]=None):
        self.last = False
        self.transitive = False
        self.duration = duration
        self.effect_draw = effect_draw

    def start(self, data: Dict):
        if EntityDataKey.DRAWING_LAYERS in data:
            if self.effect_draw is None:
                entity_draw = data[EntityDataKey.DRAWING_LAYERS][0]
                self.effect_draw = ''.join([Effect.SMOKED for _ in range(len(entity_draw))])
            if self.effect_draw not in data[EntityDataKey.DRAWING_LAYERS]:
                data[EntityDataKey.DRAWING_LAYERS].append(self.effect_draw)

    def end(self, data: Dict):
        if EntityDataKey.DRAWING_LAYERS in data:
            data[EntityDataKey.DRAWING_LAYERS].remove(self.effect_draw)

    def do(self, data: Dict, input: Input) -> Optional[Behaviour]:
        if EntityDataKey.HEALTH in data:
            data[EntityDataKey.HEALTH] -= 0.5
        if (self.duration - 1) > 0:
            return Smoked(self.duration - 1)
        else:
            return None

    def compose(self, other: Behaviour) -> Optional[Behaviour]:
        return None


class InFire(Behaviour):
    def __init__(self, duration: int, effect_draw: Optional[str]=None):
        self.last = False
        self.transitive = True
        self.duration = duration
        self.effect_draw = effect_draw

    def start(self, data: Dict):
        if EntityDataKey.DRAWING_LAYERS in data:
            if self.effect_draw is None:
                entity_draw = data[EntityDataKey.DRAWING_LAYERS][0]
                self.effect_draw = ''.join([Effect.FIRE for _ in range(len(entity_draw))])
            if self.effect_draw not in data[EntityDataKey.DRAWING_LAYERS]:
                data[EntityDataKey.DRAWING_LAYERS].append(self.effect_draw)

    def end(self, data: Dict):
        if EntityDataKey.DRAWING_LAYERS in data:
            data[EntityDataKey.DRAWING_LAYERS].remove(self.effect_draw)

    def do(self, data: Dict, input: Input) -> Optional[Behaviour]:
        if EntityDataKey.HEALTH in data:
            data[EntityDataKey.HEALTH] -= 1
        if (self.duration - 1) > 0:
            return InFire(self.duration - 1, effect_draw=self.effect_draw)
        else:
            return None

    def compose(self, other: Behaviour) -> Optional[Behaviour]:
        if isinstance(other, InFire):
            return InFire(duration=self.duration + other.duration)
        if isinstance(other, Wet):
            return Smoked(duration=3)
        else:
            return None

class Hitted(Behaviour):
    def __init__(self, duration: int=2):
        self.last = False
        self.transitive = False
        self.duration = duration
        self.effect_draw = "  H I T  "

    def start(self, data: Dict):
        if EntityDataKey.DRAWING_LAYERS in data:
            if self.effect_draw not in data[EntityDataKey.DRAWING_LAYERS]:
                data[EntityDataKey.DRAWING_LAYERS].append(self.effect_draw)

    def end(self, data: Dict):
        if EntityDataKey.DRAWING_LAYERS in data:
            data[EntityDataKey.DRAWING_LAYERS].remove(self.effect_draw)

    def do(self, data: Dict, input: Input) -> Optional[Behaviour]:
        if (self.duration - 1) > 0:
            return Hitted(self.duration - 1)
        else:
            return None

    def compose(self, other: Behaviour) -> Optional[Behaviour]:
        if isinstance(other, Hitted):
            return Hitted()
        else:
            return None

class Wet(Behaviour):
    def __init__(self, duration: int, effect_draw: Optional[str]=None):
        self.last = False
        self.transitive = False
        self.duration = duration
        self.effect_draw = effect_draw

    def start(self, data: Dict):
        if EntityDataKey.DRAWING_LAYERS in data:
            if self.effect_draw is None:
                entity_draw = data[EntityDataKey.DRAWING_LAYERS][0]
                self.effect_draw = ''.join([Effect.WET for _ in range(len(entity_draw))])
            if self.effect_draw not in data[EntityDataKey.DRAWING_LAYERS]:
                data[EntityDataKey.DRAWING_LAYERS].append(self.effect_draw)

    def end(self, data: Dict):
        if EntityDataKey.DRAWING_LAYERS in data:
            data[EntityDataKey.DRAWING_LAYERS].remove(self.effect_draw)

    def do(self, data: Dict, input: Input) -> Optional[Behaviour]:
        if (self.duration - 1) > 0:
            return Wet(self.duration - 1)
        else:
            return None

    def compose(self, other: Behaviour) -> Optional[Behaviour]:
        if isinstance(other, Wet):
            return Wet(duration=self.duration + other.duration)
        if isinstance(other, InFire):
            return Smoked(duration=self.duration - 1)
        else:
            return None
