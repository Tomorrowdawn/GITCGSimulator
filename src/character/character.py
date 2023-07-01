import sys
sys.path.append("..")

from ..core.GameState import GameState, Profile
from ..core.Listener import Listener

from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Mapping, Union, Any

class Character(metaclass = ABCMeta):
    def __init__(self, hp, energy, aura, equipment, buff, history):
        pass
    def getListeners(self)->List[Listener]:
        """按序返回装备和角色状态"""
        pass
    def equip(self, equipment)->None:
        pass
    