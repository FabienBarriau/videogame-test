from __future__ import annotations
from typing import List, Callable, Optional, Tuple, Dict, Type
from composition.behaviour import Behaviour, Positioned
from composition.constants import EntityData, Input, EntityDataKey
from .behaviour import Hitted


class Entity:
    def __init__(self, behaviours: List[Behaviour], attached_entities: Optional[List[Entity]]=None, control: Optional[Dict[str, Action]]=None):
        self.data: EntityData = {}
        self.behaviours = behaviours
        for behaviour in behaviours:
            behaviour.start(self.data)
        if attached_entities is not None:
            self.attached_entities = attached_entities
        else:
            self.attached_entities = []
        self.control = control

    @staticmethod
    def _add_new_behaviour(data: EntityData, behaviours: List[Behaviour], new_behaviour: Behaviour):
        for behaviour in behaviours:
            behaviour_composition = behaviour.compose(new_behaviour)
            if behaviour_composition is not None:
                behaviour.end(data)
                behaviours.remove(behaviour)
                behaviour_composition.start(data)
                behaviours.append(behaviour_composition)
                return behaviours
        new_behaviour.start(data)
        behaviours.append(new_behaviour)
        return behaviours

    def add_new_behaviour(self, new_behaviour: Behaviour):
        return self._add_new_behaviour(self.data, self.behaviours, new_behaviour)

    def remove_behaviour(self, behaviour_type: Type):
        to_remove = None
        for behaviour in self.behaviours:
            if isinstance(behaviour, behaviour_type):
                to_remove = behaviour
                break
        if to_remove is not None:
            to_remove.end(self.data)
            self.behaviours.remove(to_remove)

    def update(self, input: Input):
        new_behaviours: List[Behaviour] = []
        for behaviour in self.behaviours:
            new_behaviour = behaviour.do(self.data, input)
            if new_behaviour is None:
                behaviour.end(self.data)
            else:
                new_behaviours = self._add_new_behaviour(self.data, new_behaviours, new_behaviour)

        self.behaviours = sorted(new_behaviours, key=lambda behaviour: behaviour.last)

    def interact(self, world: List[Entity], action: Callable[[Entity, List[Entity]], None]):
        action(self, world)

    def __repr__(self) -> str:
        return str({
            "data": self.data,
            "behaviours": [type(behaviour) for behaviour in self.behaviours]
        })

Action = Callable[[Entity, List[Entity]], None]

def attack(attacker: Entity, world: List[Entity]):
    if EntityDataKey.POSITION in attacker.data:
        defenser_position = attacker.data[EntityDataKey.POSITION] + 1
    else:
        ValueError(f"Actual entity {attacker} must be Positioned")
    defenser = None
    for entity in world:
        if EntityDataKey.POSITION in entity.data:
            if entity.data[EntityDataKey.POSITION] == defenser_position:
                defenser = entity
                break
    
    if defenser is not None:
        if (EntityDataKey.ATTACK in attacker.data) and (
            EntityDataKey.HEALTH in defenser.data
        ):
            final_attack = attacker.data[EntityDataKey.ATTACK]
            if attacker.attached_entities:
                weapon = attacker.attached_entities[0]
                if EntityDataKey.ATTACK in weapon.data:
                    final_attack += weapon.data[EntityDataKey.ATTACK]
                    for behaviour in weapon.behaviours:
                        if behaviour.transitive:
                            defenser.add_new_behaviour(behaviour)
            defenser.add_new_behaviour(Hitted())
            defenser.data[EntityDataKey.HEALTH] = defenser.data[EntityDataKey.HEALTH] - final_attack


def move(step: int) -> Action:
    def move_to(mover: Entity, world: List[Entity]):
        if EntityDataKey.POSITION in mover.data:
            new_position = mover.data[EntityDataKey.POSITION] + step
        else:
            ValueError(f"Actual entity {mover} must be Positioned")
        entity_already_on_new_position = None
        for entity in world:
            if EntityDataKey.POSITION in entity.data:
                if entity.data[EntityDataKey.POSITION] == new_position:
                    entity_already_on_new_position = entity
                    break
        if entity_already_on_new_position is None:
            mover.data[EntityDataKey.POSITION] = new_position
    return move_to


def grab(grabber: Entity, world: List[Entity]):
    if EntityDataKey.POSITION in grabber.data:
            new_position = grabber.data[EntityDataKey.POSITION] + 1
    else:
        ValueError(f"Actual entity {grabber} must be Positioned")
    entity_to_grab = None
    for entity in world:
        if EntityDataKey.POSITION in entity.data:
            if entity.data[EntityDataKey.POSITION] == new_position:
                entity_to_grab = entity
                break

    if entity_to_grab is not None:
        grabber.attached_entities.append(entity_to_grab)
        entity_to_grab.remove_behaviour(Positioned)

def select(orientation: bool) -> Action:
    def select_to(entity: Entity, world: List[Entity]):
        entity.attached_entities
        if len(entity.attached_entities) > 1:
            if orientation:
                entity.attached_entities  = entity.attached_entities[1:] + [entity.attached_entities[0]]
            else:
                entity.attached_entities  = [entity.attached_entities[-1]] + entity.attached_entities[0:-1]
    return select_to


def draw(world: List[Entity]):        
    first_col_position_drawing: List[Tuple[int, List[str]]] = []
    second_col_position_drawing: Dict[int, List[str]] = {}
    for entity in world:
        if (EntityDataKey.POSITION in entity.data) and (EntityDataKey.DRAWING_LAYERS in entity.data):
            first_col_position_drawing.append((entity.data[EntityDataKey.POSITION], entity.data[EntityDataKey.DRAWING_LAYERS]))
            if entity.attached_entities:
                # Draw only the first attached entities
                first_attached_entities = entity.attached_entities[0]
                if EntityDataKey.DRAWING_LAYERS in first_attached_entities.data:
                        second_col_position_drawing[entity.data[EntityDataKey.POSITION]] = first_attached_entities.data[EntityDataKey.DRAWING_LAYERS]                   
    column = []
    if first_col_position_drawing:
        max_down = max(first_col_position_drawing, key=lambda item: item[0])[0]
        max_layer = len(max(first_col_position_drawing + list(second_col_position_drawing.items()), key=lambda item: len(item[1]))[1])
        column = ['|' + '        ' + '        ' + '| \n' for _ in range(max_down + 1)]
        for position, drawing_layers in first_col_position_drawing:
            toto = ''
            if position == 0:
                    toto += '================== \n'
            if position in second_col_position_drawing:
                attached_drawing_layers = second_col_position_drawing[position]
                for i in reversed(range(max_layer)):
                    if (i < len(drawing_layers)) and (i < len(attached_drawing_layers)):
                        toto += '|' + drawing_layers[i] + attached_drawing_layers[i] + '| \n'
                    elif i < len(attached_drawing_layers):
                        toto += '|' + '        ' + attached_drawing_layers[i] + '| \n'
                    elif i < len(drawing_layers):
                        toto += '|' + drawing_layers[i] + '        ' + '| \n'
                    else:
                        toto += '|' + '        ' + '        ' + '| \n'
            else:
                 for i in reversed(range(max_layer)):
                    if (i < len(drawing_layers)):
                        toto += '|' + drawing_layers[i] + '        ' + '| \n'
                    else:
                        toto += '|' + '        ' + '        ' + '| \n'
            column[position] = toto
        for row in column:
            print(row)
