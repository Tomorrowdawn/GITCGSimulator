import sys
sys.path.append("..")

from src.core.GameState import GameState, GameInstance, Profile


from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Mapping, Union, Any, Type

class Card(metaclass = ABCMeta):
    def __init__(self) -> None:
        self.vars = ['usage','round']
        self.usage = 0
        self.round = 0
        pass
    
    @property
    @abstractmethod
    def tags(self)->List[str]:
        ##
        pass
    @abstractmethod
    def play(self, g:GameInstance):
        pass
    
    def record(self, name:str):
        """调用此方法来记录该类想要自动记录的成员变量. usage和round属于默认记录对象.
        
        如, self.a = 1
        self.record('a')
        
        注意必须传入字符串. 需在__init__中调用, 并且需要在之前super().__init__().
        """
        assert type(name) == str
        self.vars.append(name)
    def export(self)->List[Tuple[str, Profile]]:
        pass
    def restore(self, paras:Profile):
        pass
    
import src.character.character as Char

class Box:
    def __init__(self, box):
        chars, cards = box
        self.chars = chars
        self.deck = cards

class Deck:
    """Deck中可能维护activated cards. 现阶段暂时不准备. 
    唯一的定向检索食品袋可以手写所有食品的集合然后取交集.
    """
    
    def __init__(self, deck:Mapping[str,int]) -> None:
        pass
    def export(self)->List[str]:
        pass
    def draw(self, num, cond = None):
        pass

class Hand(object):
    def __init__(self) -> None:
        self.hand = list()
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