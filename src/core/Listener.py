from __future__ import annotations

import sys
sys.path.append("..")
sys.path.append("../..")

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.core.GameInstance import GameInstance


from src.core.GameState import GameState, Item, Profile
from src.core.Event import Event
from typing import List, Tuple, Mapping, Union, Any
from abc import ABCMeta, abstractmethod
from src.core.base import DiceInstance, DicePattern, Location


MAX_LISTEN_VAR = 5


class Listener(metaclass = ABCMeta):
    _vars = []
    def __init__(self) -> None:
        self.alive = True
        self.loc:Location = None
        pass
    
    def record(self, name:str):
        """调用此方法来记录该类想要导出的成员变量. 
        
        如, self.a = 1
        self.record('a')
        
        之后调用export时会自动导出self.a. 装载时也会自动装载self.a
        
        注意必须传入字符串. 需在__init__中调用, 并且需要在最开头调用super().__init__().
        """
        assert type(name) == str
        self._vars.append(name)
        if len(self._vars) > MAX_LISTEN_VAR:
            raise "Too many variables! Try to remove constant like damage per hit or remove variables those only works in runtime."
    def export(self)->Item:
        pass
    def restore(self, profile:Profile):
        pass
    def listen(self, g:"GameInstance", event)->Union[List[Event], None]:
        if self.alive and event.eid != -1:
            return self.take_listen(g, event)
        return None
    def place(self, loc:Location):
        self.loc = loc
    
    @abstractmethod
    def take_listen(self, g:"GameInstance", event:Event)->Union[List[Event], None]:
        pass