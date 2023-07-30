from __future__ import annotations
import sys

sys.path.extend(['..','../..'])

from src.character.character import Character
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from src.core.GameInstance import GameInstance
    
from src.core.Event import DMGType, List, damage
import src.core.Event as Event
from src.core.base import DicePattern
from src.core.Listener import Buff, Summoned, CharBuff



class Senho(CharBuff):
    init_usage = 1
    def __init__(self) -> None:
        self.fusion = False
        super().__init__()
    def take_listen(self, g: GameInstance, event) -> List[Event.Event]:
        if type(event) != Event.Over:
            if type(event) != Event.DMGTypeCheck:
                if type(event) == Event.StartPhase:
                    self.fusion = False
                return []
            else:
                if not self.fusion:
                    return []
                for dmg in event.dmg_list:
                    if dmg.attacker == self.loc and dmg.dmgtype == DMGType.physical:
                        dmg.dmgtype = DMGType.cryo
                return []
        event:Event.Over
        if event.eid == 0:
            self.fusion = True
        if type(event.overed) != Event.Switch:
            return []
        if event.overed.succeed:
            active = g.getactive(self.loc.player_id)
            if active.index == self.loc.index:
                self.fusion = True
        return []

class Frostflake(Summoned):
    init_usage = 2
    dtype = DMGType.cryo
    dvalue = 2

class Ayaka(Character):
    maxhp = 10
    maxenergy = 3
    faction = 'Inazuma'
    weapontype = 'Sword'
    element = 'cryo'
    
    dice_cost = {
        'na':DicePattern(cryo=1,black=2),
        'skill':DicePattern(cryo=3),
        'burst':DicePattern(cryo=3),
    }
    no_charge = []
    
    def passive(self, g):
        ccb = Event.CreateCharBuff(g.nexteid(),-1,self.loc.player_id, self.loc, Senho)
        return [ccb]
    
    def na(self,g:GameInstance):
        dmg_list = g.make_damage(self.loc.player_id, 'active',2,DMGType.physical)
        return [Event.RawDMG(g.nexteid(),-1,self.loc.player_id,dmg_list),]
    def skill(self,g:GameInstance):
        dmg_list = g.make_damage(self.loc.player_id, 'active',3,DMGType.cryo)
        return [Event.RawDMG(g.nexteid(),-1,self.loc.player_id,dmg_list),]
    def burst(self,g:GameInstance):
        dmg_list = g.make_damage(self.loc.player_id, 'active',4,DMGType.cryo)
        pid = self.loc.player_id
        dmg =  Event.RawDMG(g.nexteid(),-1,pid,dmg_list)
        summon = Event.Summon(g.nexteid(), -1 ,pid, pid , Frostflake)
        return [summon, dmg]
    def sp1(self,g):
        pass
    def sp2(self,g):
        pass