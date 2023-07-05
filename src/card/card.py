from __future__ import annotations

import sys
sys.path.append("..")
sys.path.append("../..")

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.core.GameInstance import GameInstance


from src.core.GameState import GameState, Profile
from src.core.Event import Event

from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Mapping, Union, Any, Type

class Card(metaclass = ABCMeta):
    
    @property
    @abstractmethod
    def tags(self)->List[str]:
        ##
        pass
    @abstractmethod
    def play(self, g:GameInstance)->List[Event]:
        pass
    
    @abstractmethod
    def valid(self, g:GameInstance)->bool:
        pass
    
import src.character.character as Char
import random

class Deck:
    """Deck中可能维护activated cards. 现阶段暂时不准备. 
    唯一的定向检索食品袋可以手写所有食品的集合然后取交集.
    """
    
    def __init__(self, deck:Mapping[str,int] = None) -> None:
        if deck is None:
            self.pile = []
        else:
            pass
        pass
    def export(self)->List[str]:
        pass
    def __getitem__(self, index):
        return self.pile[index]
    def draw(self, num, tags = None)->List[str]:
        pass
    def swapin(self, cards:List[str]):
        pass
    

class Hand(object):
    def __init__(self, hand:List[str]) -> None:
        self.hand = hand
    def __getitem__(self, index):
        return self.hand[index]
    def export(self):
        return self.hand
    def add(self, card:str):
        self.hand.append(card)
    def pick(self, index:int)->Card:
        c = self.hand.pop(index)
        return name2card(c)
    def __len__(self):
        return len(self.hand)

def name2card(*args)->Card:
    pass