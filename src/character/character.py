import sys
sys.path.append("..")

from src.core.GameState import GameState, Profile
from src.core.Listener import Listener

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

import src.character as chr
###对这个模块执行反射函数即可.
##要更新模块.

def name2char(*args):
    pass