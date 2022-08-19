from select import select
from composition.behaviour import Attacker, Drawable, Alive, InFire, Wet, Positioned, Dead
from composition.entity import Entity, draw, move, attack, grab, select
from composition.constants import Sprite

def run():
    fire_sword = Entity(
    [Drawable(drawing=Sprite.SWORD), Attacker(init_attack=1), InFire(duration=20), Positioned(2)]
    )
    lance = Entity(
    [Drawable(drawing=Sprite.LANCE), Attacker(init_attack=1), Positioned(3)]
    )
    player = Entity(
        [Alive(init_health=1), Drawable(drawing=Sprite.PLAYER), Attacker(init_attack=1), Positioned(0)],
        control={
            "z": move(-1),
            "s": move(1),
            "a": attack,
            "g": grab,
            "w": (lambda e, w: None), # wait
            "q": select(False),
            "d": select(True)
        }
    )
    monster = Entity(
        [
            Alive(init_health=10),
            Drawable(drawing=Sprite.BEAR),
            Positioned(4),
            Wet(duration=20)
        ]
    )
    world = [player, monster, fire_sword, lance]
    cemetery = []
    while(True):
        print("z, s: move up and down \n")
        print("a: attack \n")
        print("w: wait \n")
        print("g: grab \n")
        print("q, d: select item\n")
        print("other: quit")
        draw(world)
        user_input = input()
        if user_input not in ["z", "s", "a", "w", "g", "d", "q"]:
            exit(1)

        for entity in world:
            if entity.control is not None:
                entity.interact(world, entity.control[user_input])

        for entity in world:
            entity.update(user_input)

        to_remove = []
        for entity in world:
            for behaviour in entity.behaviours:
                if isinstance(behaviour, Dead):
                    to_remove.append(entity)
                    break
        
        for entity in to_remove:
            world.remove(entity)
            cemetery.append(entity)
                
        

if __name__ == "__main__":
    run()
