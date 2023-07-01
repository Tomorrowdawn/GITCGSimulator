"""
本代码实现事件处理框架以及事件执行(分派)函数.
"""

from Event import Event
from Listener import Listener
from GameState import GameState, GameInstance


class EventHub:
    """处理事件流程"""
    def process(self, g:GameState, event:Event)->GameState:
        GI = GameInstance(g)
        GI = self._handle(GI,event)
        GI.rebuild()
        return GI.export()
    def _handle(self, g:GameInstance, event:Event)->GameInstance:
        ###for listener in L:
        ###      if listener.listen(event) is not None:
        ###          handle(new events by order)
        ###execute event.
        ###if event is not Over:
        ###NGS = handle(Over(event))
        ###return new GameState
        pass
    pass