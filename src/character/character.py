import sys
sys.path.append("..")

from src.core.GameState import GameState, Profile, Item
from src.core.Listener import Listener

from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Mapping, Union, Any
from enum import Enum

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

class Character(metaclass = ABCMeta):
    def __init__(self):
        pass
    def getListeners(self)->List[Listener]:
        """按序返回装备和角色状态"""
        pass
    def export(self)->List[Item]:
        pass
    def restore(self, profile:Profile):
        """profile顺序同CharIndexer
        """
        pass
    
    def equip(self, equipment)->None:
        pass
    
    
    @property
    @abstractmethod
    def maxhp(self):
        raise NotImplementedError
    
    @property
    @abstractmethod
    def maxenergy(self):
        raise NotImplementedError
