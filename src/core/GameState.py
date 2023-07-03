from dataclasses import dataclass, asdict
from typing import Tuple, List, Any, Mapping, Union
from src.card.card import Card, Deck, Box, Hand
from src.character.character import Character, CharIndexer
from src.character.utils import name2char
from Event import *
import numpy as np
from copy import deepcopy
from abc import ABCMeta, abstractmethod
from base import DiceInstance,DicePattern, Location

Paras = List[Union[int, bool, str]]
Profile = List[Union[Any, Paras]]
Item = Tuple[str, Profile]

class DicePool:
    pass

class PlayerState:
    def __init__(self, box:Union[Box,None]):
        if box is None:
            return
        deck = box.deck
        #chars = box.chars
        deck = Deck(deck).export()
        
        self.deck = deck###list of str.
        self.hand = []##list of str
        
        
        ## list of (cls,profile). 即(class, parameters)形式

        self.char = []###需要char那边提供工具函数将其转换成标准形式. box中只有str信息.
        self.teambuff = []
        self.support = []
        self.summon = []
        self.dice = DiceInstance()
        self.history = {
            'dieThisRound':False
        }
        pass
    def clone(self):
        return deepcopy(self)
        pass
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
    def put(self, loc:Location, item:Item):
        """将loc所指向的地方替换成item.
        
        与get同步使用. 先get内容, 在外部完成修改, 然后put回来.
        如果loc处没有东西, 将引发错误. 特别地, 装备可以忽略此问题(因为装备是定长区域)
        """
        pass
    def add(self, loc:Location, item:Item):
        """
        新增一个item. 根据loc的倒数第二个指标确定位置. (area/subarea). 最后一个下标将自动补齐.
        特别地, 装备和put的表现一样.
        """
        pass
    def numpy(self)->np.ndarray:
        pass

class GameState:
    def __init__(self,box1:Box, box2:Box):
        self.history = {
            'rounds':1, 'mover':1
        }
        self.players = [PlayerState(box1), PlayerState(box2)]
        pass
    def clone(self):
        pass
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
      
from functools import singledispatchmethod

MAX_LISTEN_VAR = 5

class Listener(metaclass = ABCMeta):
    def __init__(self) -> None:
        self.alive = True
        self.vars = []
        pass
    
    def record(self, name:str):
        """调用此方法来记录该类想要导出的成员变量. 
        
        如, self.a = 1
        self.record('a')
        
        之后调用export时会自动导出self.a. 装载时也会自动装载self.a
        
        注意必须传入字符串. 需在__init__中调用, 并且需要在最开头调用super().__init__().
        """
        assert type(name) == str
        self.vars.append(name)
        if len(self.vars) > MAX_LISTEN_VAR:
            raise "Too many variables! Try to remove constant like damage per hit or remove variables those only works in runtime."
    def export(self)->List[Item]:
        pass
    def restore(self, profile:Profile):
        pass
    def listen(self, g:"GameInstance", event)->Union[List[Event], None]:
        if self.alive:
            return self.take_listen(g, event)
        return None
    
    @abstractmethod
    def take_listen(self, g:"GameInstance", event:Event)->Union[List[Event], None]:
        pass

from enum import Enum, IntEnum, auto

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
    anemo = 6
    geo = 7
    crydendro = 8
    died = 9

class PlayerInstance:
    def __init___(self, g:PlayerState):
        self.deck = Deck(g.deck)
        self.hand = Hand(g.hand)
        self.char = [name2char(char).restore(profile)  for char, profile in g.char]
        self.dice = DicePool(g.dice)
        #self.teambuff
        #self.support
        #self.summon
        ##TODO:
        pass
    def getListeners(self)->List[Listener]:
        pass
    def getAura(self)->List[Aura]:
        pass

class GameInstance:
    """提供方便的接口修改游戏状态, 执行事件,并可以导出GameState"""
    def __init__(self,g:GameState) -> None:
        #self.g = g.clone()
        #不能直接存, 因为GameInstance是要修改状态的, 而GameState是只读的.
        ## 需要读成GameInstance的内部格式.
        self.maxid = 0
        """TODO:激活所有类"""
        
        """
        包括Deck,Hand, 全部要读入对应类中.
        """
        self.p1 = PlayerInstance(g.players[0])
        self.p2 = PlayerInstance(g.players[1])
        self.history = g.history
        
        
    def rebuild(self)->None:
        """检查所有监听器并删掉alive=False的
        
        注意, 监听器alive只有在discard事件被执行后才能被更改. 
        """
        pass
    def getListeners(self, player_id)->List[Listener]:
        if player_id == 1:
            return self.p1.getListeners() + self.p2.getListeners()
        else:
            return self.p2.getListeners() + self.p1.getListeners()
    def getAura(self, player_id)->List[Aura]:
        pass
    def export(self)->GameState:
        #return self.g.clone()
        ##需要将各个监听器的数据统一导出而非clone.
        pass
    def nexteid(self)->int:
        self.maxid += 1
        return self.maxid
    @singledispatchmethod
    def execute(self, event)->Union[List[Event],None]:
        ##这里使用分派.
        pass
    
    @execute.register
    def dmgtypecheck(self, event:DMGTypeCheck):
        ###这里检查是否会发生反应并发射反应事件（如果有）。
        pass
    