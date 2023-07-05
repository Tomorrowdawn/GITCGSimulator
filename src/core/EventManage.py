"""
本代码实现事件处理框架以及事件执行(分派)函数.
"""

from src.core.Event import Event, Over
from src.core.Listener import Listener
from src.core.GameState import GameState
from src.core.GameInstance import GameInstance


class EventHub:
    """处理事件流程"""
    def process(self, g:GameInstance, event:Event)->GameInstance:
        g = self._handle(g,event)
        g.rebuild()
        return g
    def _handle(self, g:GameInstance, event:Event)->GameInstance:
        """强制性只执行一个事件, 每次执行完毕后整理好游戏状态.
        这样可以避免监听器修改问题.
        """
        if event.eid == -1:
            return g
        for listener in g.getListeners(event.player_id):
            ne = listener.listen(g, event)
            for e in ne:
                g = self._handle(g, e)
        ne = g._execute(event)
        for e in ne:
            g = self._handle(g, e)
        if event.eid != -1 and type(event) is not Over:
            nid = g.nexteid()
            g = self._handle(g, Over(nid, event.eid, event.player_id))
        return g
        ###for listener in L:
        ###      if listener.listen(event) is not None:
        ###          handle(new events by order)
        ###execute event.
        ###if new events
        ### handle(new events)
        ###if event is not Over:
        ###NGS = handle(Over(event))
        ###return new GameState
        pass
    pass