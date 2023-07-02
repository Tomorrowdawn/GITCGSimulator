import sys
sys.path.append("..")

from GameState import GameState
from Event import Event
from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Mapping, Union, Any


class Listener(metaclass = ABCMeta):
    def __init__(self) -> None:
        self.alive = True
        pass
    
    def listen(self, g, event)->Union[List[Event], None]:
        if self.alive:
            return self.take_listen(g, event)
        return None
    
    @abstractmethod
    def take_listen(self, g:GameState, event:Event)->Union[List[Event], None]:
        pass