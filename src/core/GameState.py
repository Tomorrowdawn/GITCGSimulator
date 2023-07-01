from dataclasses import dataclass, asdict
from typing import Tuple, List, Any, Mapping, Union
from ..card.card import Card, Deck
from Event import Event
import numpy as np


@dataclass
class Location:
    player_id:int
    area:str
    index:int
    
    ###仅用于装备/角色状态定位
    subarea:str
    offset:int
    
@dataclass
class DiceInstance:
    omni:int = 0
    pyro:int = 0
    cryo:int = 0
    hydro:int = 0
    electro:int = 0
    dendro:int = 0
    anemo:int = 0
    geo:int = 0
    
    def to_dict(self):
        return asdict(self)
    
@dataclass
class DicePattern:
    pyro:int = 0
    cryo:int = 0
    hydro:int = 0
    electro:int = 0
    dendro:int = 0
    anemo:int = 0
    geo:int = 0
    black:int = 0
    white:int = 0
    def to_dict(self):
        return asdict(self)

Profile = Tuple[str,List[Any]]

class GameState:
    def __init__(self, deck1:Deck, deck2:Deck):
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
    def getHistory(self, player_id):
        pass
    def numpy(self)->np.ndarray:
        pass
    
from Listener import Listener    
from functools import singledispatchmethod

class GameInstance:
    """提供方便的接口修改游戏状态, 执行事件,并可以导出GameState"""
    def __init__(self,g:GameState) -> None:
        self.g = g.clone()
    def rebuild(self)->None:
        """检查所有监听器并删掉已经耗尽次数(alive=False)的"""
        pass
    def getListeners(self, player_id)->List[Listener]:
        pass
    def getAura(self, player_id)->List[str]:
        pass
    def export(self)->GameState:
        return self.g.clone()
    
    @singledispatchmethod
    def execute(self, event):
        ##这里使用分派.
        pass
    
    