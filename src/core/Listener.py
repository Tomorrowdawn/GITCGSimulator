import sys
sys.path.append("..")

from GameState import GameState
from Event import Event
from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Mapping, Union, Any


class Listener(metaclass = ABCMeta):
    @abstractmethod
    def listen(self, g:GameState, event:Event)->Union[List[Event], None]:
        pass