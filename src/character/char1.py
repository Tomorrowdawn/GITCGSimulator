from __future__ import annotations
import sys
sys.path.extend(['..','../..'])

from src.character.character import Character
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from src.core.GameInstance import GameInstance
    
from src.core.Event import DMGType, Event, List, damage
import src.core.Event as Event
from src.core.base import DicePattern, samecharcheck
from src.core.Listener import Buff, Summoned, CharBuff

class Diluc(Character):
    maxhp = 10
    maxenergy = 3
    faction = 'Mondstadt'
    weapontype = 'Claymore'
    element = 'pyro'
    
    dice_cost = {
        'na':DicePattern(pyro=1,black=2),
        'skill':DicePattern(pyro=3),
        'burst':DicePattern(pyro=4),
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
    _vars = ['usage','dtype']
    def take_listen(self, g: GameInstance, event: Event.Event) -> List[Event]:
        endphase_dmg = super().take_listen(g, event)
        #event:Event.Reaction
        if self.dtype == DMGType.anemo and type(event) == Event.Reaction and event.reaction_name == 'swirl':
            if event.location.player_id != self.loc.player_id:
                self.dtype = event.trigger_element
        return endphase_dmg

class Sucrose(Character):
    maxhp = 10
    maxenergy = 2
    faction = 'Mondstadt'
    weapontype = 'Catalyst'
    element = 'anemo'
    
    dice_cost = {
        'na':DicePattern(anemo=1,black=2),
        'skill':DicePattern(anemo=3),
        'burst':DicePattern(anemo=3),
    }
    no_charge = []
    def na(self,g):
        dmg_list = g.make_damage(self.loc.player_id, 'active',1,DMGType.anemo)
        return [Event.RawDMG(g.nexteid(),-1,self.loc.player_id,dmg_list),]
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
        summon = Event.Summon(g.nexteid(), -1 ,pid, pid , LargeWindSpirit)
        return [summon, dmg]
    def sp1(self,g):
        pass
    def sp2(self,g):
        pass
    pass

class GlacialWaltz(Buff):
    init_usage = 3
    def __init__(self):
        self.switch_id = -2
        #self.record('switch_id')
        super().__init__()
    def take_listen(self, g: GameInstance, event: Event) -> List[Event]:
        if type(event) is Event.Switch and event.char_loc.player_id == self.loc.player_id:
            self.switch_id = event.eid
            return []
        elif type(event) == Event.Over:
            #print(self.__dict__)
            if event.overed.eid == self.switch_id:
                es = []
                if event.overed.succeed:
                    oppo_active = g.getactive(3-self.loc.player_id)
                    dmg = damage(self.loc, oppo_active, DMGType.cryo, 2)
                    es.append(Event.RawDMG(g.nexteid(),event.eid,self.loc.player_id,[dmg]))
                    self.usage -= 1
                if self.usage <= 0:
                    self.alive = False
                self.switch_id = -2
                return es
            else:
                return []
        else:
            return []

class Kaeya(Character):
    maxhp = 10
    maxenergy = 2
    faction = 'Mondstadt'
    weapontype = 'Sword'
    element = 'cryo'
    
    dice_cost = {
        'na':DicePattern(cryo=1,black=2),
        'skill':DicePattern(cryo=3),
        'burst':DicePattern(cryo=4),
    }
    no_charge = []
    
    def na(self,g:GameInstance):
        dmg_list = g.make_damage(self.loc.player_id, 'active',2,DMGType.physical)
        return [Event.RawDMG(g.nexteid(),-1,self.loc.player_id,dmg_list),]
    def skill(self,g:GameInstance):
        dmg_list = g.make_damage(self.loc.player_id, 'active',3,DMGType.cryo)
        return [Event.RawDMG(g.nexteid(),-1,self.loc.player_id,dmg_list),]
    def burst(self,g:GameInstance):
        dmg_list = g.make_damage(self.loc.player_id, 'active',1,DMGType.cryo)
        dmg = Event.RawDMG(g.nexteid(),-1,self.loc.player_id,dmg_list)
        buff = Event.CreateBuff(g.nexteid(),-1,self.loc.player_id, self.loc.player_id, GlacialWaltz)
        return [dmg, buff]
    def sp1(self,g):
        pass
    def sp2(self,g):
        pass

class Oz(Summoned):
    init_usage = 2
    dtype = DMGType.electro
    dvalue = 1
    
class Fischl(Character):
    maxhp = 10
    maxenergy = 3
    faction = 'Mondstadt'
    weapontype = 'Bow'
    element = 'electro'
    
    dice_cost = {
        'na':DicePattern(electro=1,black=2),
        'skill':DicePattern(electro=3),
        'burst':DicePattern(electro=3),
    }
    no_charge = []
    
    def na(self,g:GameInstance):
        dmg_list = g.make_damage(self.loc.player_id, 'active',2,DMGType.physical)
        return [Event.RawDMG(g.nexteid(),-1,self.loc.player_id,dmg_list),]
    def skill(self,g:GameInstance):
        dmg_list = g.make_damage(self.loc.player_id, 'active',1,DMGType.electro)
        dmg = Event.RawDMG(g.nexteid(),-1,self.loc.player_id,dmg_list)
        summon = Event.Summon(g.nexteid(),-1, self.loc.player_id, self.loc.player_id, Oz)
        return [dmg, summon]
    def burst(self,g:GameInstance):
        dmg_list = g.make_damage(self.loc.player_id, 'active',4,DMGType.electro)
        dmg_list += g.make_damage(self.loc.player_id, 'standby', 2, DMGType.pierce)
        dmg = Event.RawDMG(g.nexteid(),-1,self.loc.player_id,dmg_list)
        return [dmg,]
    def sp1(self,g):
        pass
    def sp2(self,g):
        pass

class ExplosiveSpark(CharBuff):
    init_usage = 1
    is_shield = False
    def __init__(self) -> None:
        super().__init__()
        self.naid = -1
        self.dpcusage = self.usage
    def _reducedice(self, g:GameInstance, event, e):
        """
        e是usekit事件
        event是外包装,可以是DiceWrap也可以是DicePrecal
        """
        
        if type(e) is not Event.UseKit:
            return False
        e:Event.UseKit
        pds = g._getpds(event.player_id)
        if pds.dice.num() % 2 != 0:
            return False
        if not samecharcheck(e.cur_char, self.loc):
            return False
        if e.kit_type != 'na':
            return False
        if event.dice_pattern.pyro > 0:
            event.dice_pattern.pyro -= 1
        elif event.dice_pattern.black > 0:
            event.dice_pattern.black -= 1
        return True
    def take_listen(self, g: GameInstance, event) -> List[Event]:
        if type(event) is Event.DicePreCal:
            self.dpcusage = self.usage
            if self.dpcusage > 0:
                self._reducedice(g, event, event.event_instance)
                return []
            return []
        if type(event) is Event.DiceWrap:
            ###注意我们不希望在这里discard,所以就算usage = 0也不要急着alive=False
            if self.usage > 0:
                if self._reducedice(g, event, event.origin_event):
                    self.usage -= 1
                    e = event.origin_event
                    self.naid = e.eid
                    return []
            else:
                return []
        if type(event) is Event.DMG:
            if event.source_id == self.naid:
                e:Event.DMG = event
                e.dmg_list[0].dmgvalue += 1
            return []
        if type(event) is Event.Over and event.overed.eid == self.naid:
            self.naid = -1
            self.alive = False
            return []
if __name__ == "__main__":
    D = Diluc()
    from src.core.base import Location
    D.place(Location(1,'Char',1))
    from src.core.GameState import GameState
    G = GameInstance(None)
    print(D.na(G))