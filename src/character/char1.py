from __future__ import annotations
import sys
sys.path.extend(['..','../..'])

from src.character.character import Character
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.core.GameInstance import GameInstance
    
from src.core.Event import DMGType
import src.core.Event as Event
from src.core.base import DicePattern

class Diluc(Character):
    maxhp = 10
    maxenergy = 3
    faction = 'Mondstadt'
    weapontype = 'Claymore'
    element = 'pyro'
    
    dice_cost = {
        'na':DicePattern(pyro=1,black=2),
        'skill':DicePattern(pyro=3),
        'busrt':DicePattern(pyro=4),
    }
    no_charge = []
    
    def na(self,g:GameInstance):
        dmg_list = g.make_damage('active',2,DMGType.physical)
        return [Event.RawDMG(g.nexteid(),-1,self.loc.player_id,dmg_list),]
    def skill(self,g:GameInstance):
        pass
    def burst(self,g:GameInstance):
        pass
    def sp1(self,g):
        pass
    def sp2(self,g):
        pass

class Sucrose(Character):
    def na(self,g):
        pass
    def skill(self,g):
        pass
    def burst(self,g):
        pass
    def sp1(self,g):
        pass
    def sp2(self,g):
        pass
    pass

class Kaeya(Character):
    maxhp = 10
    def na(self,g):
        pass
    def skill(self,g):
        pass
    def burst(self,g):
        pass
    def sp1(self,g):
        pass
    def sp2(self,g):
        pass

if __name__ == "__main__":
    D = Diluc()
    from src.core.base import Location
    D.place(Location(1,'Char',1))
    from src.core.GameState import GameState
    G = GameInstance(None)
    print(D.na(G))