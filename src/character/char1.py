from __future__ import annotations
import sys
sys.path.extend(['..','../..'])

from src.character.character import Character
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.core.GameInstance import GameInstance
    
from src.core.Event import DMGType, damage
import src.core.Event as Event
from src.core.base import DicePattern
from src.core.Listener import Buff, Summoned

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
        dmg_list = g.make_damage(self.loc.player_id, 'active',2,DMGType.physical)
        return [Event.RawDMG(g.nexteid(),-1,self.loc.player_id,dmg_list),]
    def skill(self,g:GameInstance):
        dmg_list = g.make_damage(self.loc.player_id, 'active',3,DMGType.pyro)
        if self.history['skill_use_round'] == 3:
            #dmg_list:list[damage]
            dmg_list[0].dmgvalue += 2
        return [Event.RawDMG(g.nexteid(),-1,self.loc.player_id,dmg_list),]
    def burst(self,g:GameInstance):
        dmg_list = g.make_damage(self.loc.player_id, 'active',8,DMGType.pyro)
        return [Event.RawDMG(g.nexteid(),-1,self.loc.player_id,dmg_list),]
    def sp1(self,g):
        pass
    def sp2(self,g):
        pass


class LargeWindSpirit(Summoned):
    init_usage = 3
    dtype = DMGType.anemo
    dvalue = 2
    pass

class Sucrose(Character):
    maxhp = 10
    maxenergy = 3
    faction = 'Mondstadt'
    weapontype = 'Catalyst'
    element = 'anemo'
    
    dice_cost = {
        'na':DicePattern(anemo=1,black=2),
        'skill':DicePattern(anemo=3),
        'busrt':DicePattern(anemo=3),
    }
    no_charge = []
    def na(self,g):
        dmg_list = g.make_damage(self.loc.player_id, 'active',1,DMGType.anemo)
        return [Event.RawDMG(g.nexteid(),-1,self.loc.player_id,dmg_list),]
        pass
    def skill(self,g:GameInstance):
        dmg_list = g.make_damage(self.loc.player_id, 'active',3,DMGType.anemo)
        pid = self.loc.player_id
        dmg =  Event.RawDMG(g.nexteid(),-1,pid,dmg_list)
        oppo = g.getactive(3 - pid)
        switch = Event.Switch(g.nexteid(), -1, pid, oppo, -1)
        return [switch, dmg]
    def burst(self,g):
        dmg_list = g.make_damage(self.loc.player_id, 'active',1,DMGType.anemo)
        pid = self.loc.player_id
        dmg =  Event.RawDMG(g.nexteid(),-1,pid,dmg_list)
        summon = Event.Summon(g.nexteid(), -1 ,pid, LargeWindSpirit)
        return [dmg, summon]
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