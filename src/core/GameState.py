import sys
sys.path.append("..")
sys.path.append("../..")

from dataclasses import dataclass, asdict
from typing import Tuple, List, Any, Mapping, Union, TypedDict
from src.core.Event import *

import numpy as np
from copy import deepcopy
from abc import ABCMeta, abstractmethod
from src.core.base import DiceInstance,DicePattern, Location
from enum import IntEnum

Paras = List[Union[int, bool, str]]
Profile = List[Union[Any, Paras]]
Item = Tuple[str, Profile]


AuraList = ['empty','pyro','cryo','electro','hydro',
            'dendro','anemo','geo','crydendro','died']
#Aura = IntEnum('Aura',AuraList,start = 0)

class Aura(IntEnum):
    empty = 0
    pyro = 1
    cryo = 2
    electro = 3
    hydro = 4
    dendro = 5
    crydendro = 6
    anemo = 7
    geo = 8
    died = 9

CharIndexer = {
    'hp':0,
    'energy':1,
    'aura':2,
    'weapon':3,
    'artifact':4,
    'talent':5,
    'buff':6,
    'history':7
}

class Box:
    def __init__(self, chars, cards):
        self.chars = chars
        self.deck = cards###TODO: 使用dict形式


class PlayerState:
    class History(TypedDict):
        dieThisRound:bool
        active:int
        plunge:bool
        player_id:int
        endround:bool
    def __init__(self, box:Union[Box,None] = None):
        if box is None:
            return
        deck = box.deck
        #chars = box.chars
        #deck = Deck(deck).export()
        
        self.deck = deck###dict[str, int]
        self.hand = []##list of str
        
        
        ## list of (cls,profile). 即(class, parameters)形式
        self.char = box.chars###需要char那边提供工具函数将其转换成标准形式. box中只有str信息.
        self.teambuff = []
        self.support = []
        self.summon = []
        self.dice = DiceInstance()
        self.history:PlayerState.History = {
            'dieThisRound':False,'active':-1,'plunge':False,'player_id':-1,
            'endround':False
        }
        ##active:出战角色下标
        ##plunge:切人后将其置为True. 执行一次技能后将其置为False.
        #player_id需要外部赋值. 
        pass
    def clone(self):
        return deepcopy(self)
    def get(self, loc:Location)->Union[Any, List[Item], None]:
        area = loc.area
        if area != 'Char':
            area = area.lower()
            Area = self.__dict__[area]
            return Area[loc.index]
        else:
            Area = self.char
            char = Area[loc.index]
            if loc.subarea == '':
                return char
            elif loc.subarea != 'buff':
                idx = CharIndexer[loc.subarea]
                _, profile = char
                return profile[idx]
            else:
                idx = CharIndexer['buff']
                _,profile = char
                buff = profile[idx]
                return buff[loc.offset]
    def numpy(self)->np.ndarray:
        pass

from typing import TypedDict
import pickle
class GameState:
    class History(TypedDict):
        rounds:int
        mover:int
        phase:str
        winner:str
    def __init__(self,box1:Box = None, box2:Box=None):
        self.history = {
            'rounds':1, 'mover':1, 'phase':'firstfive','winner': -1
        }
        ###phase:
        ###firstfive, roll, start, combat, end, deathswitch
        if box1 is not None:
            self.players = [PlayerState(box1), PlayerState(box2)]
        else:
            self.players = []
    def clone(self):
        #g = GameState()
        #g.history = deepcopy(self.history)
        #g.players = [p.clone() for p in self.players]
        return pickle.loads(pickle.dumps(self))
    def get(self, loc:Location)->Union[Profile, None]:
        pass
    def getChar(self, player_id)->List[Profile]:
        pass
    def getTeambuff(self, player_id)->List[Profile]:
        pass
    def getSummon(self, player_id)->List[Profile]:
        pass
    def getSupport(self, player_id)->List[Profile]:
        pass
    def getDice(self, player_id)->DiceInstance:
        pass
    def getHistory(self)->dict:
        return self.history
        pass
    def numpy(self)->np.ndarray:
        pass