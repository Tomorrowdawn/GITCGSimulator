from __future__ import annotations

import sys
sys.path.append("..")
sys.path.append("../..")

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.core.GameInstance import GameInstance
    
from src.core.Listener import Listener
from src.core.base import Location, DiceInstance,DicePattern
from src.core.error import LocationError
from src.core.GameState import GameState, Profile, Item, CharIndexer, Aura

from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Mapping, Union, Any,TypedDict
from enum import Enum
import src.core.Event as Event
import pickle

class Character(metaclass = ABCMeta):
    class History(TypedDict):
        na_use_round:int
        na_use_total:int
        
        skill_use_round:int
        skill_use_total:int
        
        burst_use_round:int
        burst_use_total:int
        
        sp1_use_round:int
        sp1_use_total:int
        
        sp2_use_round:int
        sp2_use_total:int
        
        frozen:bool
        petrified:bool
        saturated:bool
        pass
    def __init__(self):
        self.loc:Location = None
        self.hp = self.maxhp
        self.energy = 0
        self.aura = Aura.empty
        self.weapon:Listener = None
        self.artifact:Listener = None
        self.talent:Listener = None
        self.buff:List[Listener] = []
        self.history:Character.History = {'frozen':False,'petrified':False,'saturated':False}
        for name in ['na','skill','burst','sp1','sp2']:
            self.history[name+'_use_round'] = 0
            self.history[name+'_use_total'] = 0
        pass
    def startphase_reset(self):
        self.history['frozen'] = False
        self.history['petrified'] = False
        self.history['saturated'] = False
        for name in ['na','skill','burst','sp1','sp2']:
            self.history[name+'_use_round'] = 0
    def getListeners(self)->List[Listener]:
        """按序返回装备和角色状态"""
        if self.hp <= 0:
            return []
        ls = [self.weapon, self.artifact, self.talent]
        ls = [i for i in ls if i is not None]
        return ls + self.buff
    def export(self)->Item:
        items = [self.hp, self.energy, self.aura]
        for compo in ['weapon','artifact','talent']:
            if getattr(self,compo) == None:
                items.append(None)
            else:
                items.append(getattr(self, compo).export())
        buffs = [buff.export() for buff in self.buff]
        items.append(buffs)###这里千万不能extend
        items.append(pickle.loads(pickle.dumps(self.history)))
        return (type(self).__name__, items)
    def restore(self, profile:Profile):
        """profile顺序同CharIndexer
        
        外部调用后一定要用place分配location.
        """
        hp, energy, aura, weapon, artifact, talent, charbuff, history = profile
        
        self.hp = hp
        self.energy = energy
        self.aura = aura
        self.history = history
        
        ##TODO: 剩下四个需要转换. 特别地, charbuff是一个list.
        ## 别忘了place!
        pass
    def died(self)->bool:
        return self.hp <= 0
    def equip(self, equipment)->None:
        pass
    def createListener(self, listener:Listener, loc:Location):
        """根据loc倒数第二个有效下标分配"""
        if loc.subarea == 'weapon':
            self.weapon = listener
            self.weapon.place(loc)
        elif loc.subarea == 'artifact':
            self.artifact = listener
            self.artifact.place(loc)
        elif loc.subarea == 'talent':
            self.talent = listener
            self.talent.place(loc)
        elif loc.subarea == 'buff':
            bname = type(listener).__name__
            found = False
            for i, b in enumerate(self.buff):
                exist_name = type(b).__name__
                if bname == exist_name:
                    listener.place(b.loc)
                    self.buff[i] = listener
                    found = True
                    break
            if not found:
                index = len(self.buff)
                loc.index = index
                listener.place(loc)
                self.buff.append(listener)
        else:
            raise LocationError("unavailable subarea value")
    def place(self, loc:Location):
        self.loc = loc
    def injure(self, dvalue, source_id, g:GameInstance)->List[Event.Event]:
        self.hp = max(0, self.hp - dvalue)
        if self.hp == 0:
            eid = g.nexteid()
            return [Event.Death(eid,source_id, self.loc.player_id, self.loc),]
        return []
    def heal(self, hvalue, source_id, g:GameInstance):
        self.hp = min(self.hp+hvalue, self.maxhp)
    def charge(self, cvalue, source_id, g:GameInstance):
        self.energy += cvalue
        self.energy = max(0, self.energy)
        self.energy = min(self.energy, self.maxenergy)
    
    maxhp = 10
    maxenergy = 0
    weapontype = 'Sword'
    faction = 'Mondstadt'
    element = 'electro'
    
    skill_type = {
        'na':'na',
        'skill':'skill',
        'burst':'burst'
    }
    
    no_charge = []
    
    dice_cost = {
        'na':None,'skill':None,'burst':DicePattern()
    }
    
    @abstractmethod
    def na(self,g):
        pass
    
    @abstractmethod
    def skill(self,g):
        pass
    
    @abstractmethod
    def burst(self,g):
        pass
    
    @abstractmethod
    def sp1(self,g):
        pass
    
    @abstractmethod
    def sp2(self,g):
        pass
    