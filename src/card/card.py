import sys
sys.path.append("..")

from ..core.GameState import GameState


from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Mapping, Union, Any
class Card(metaclass = ABCMeta):
    @property
    @abstractmethod
    def labels(self)->List[str]:
        ##
        pass
    @abstractmethod
    def play(self, g:GameState):
        pass
    
class Deck:
    def __init__(self, deck:Mapping[str,int]) -> None:
        pass