"""
本代码实现事件处理框架以及事件执行(分派)函数.
"""

from Event import Event, Over
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
        """强制性只执行一个事件, 每次执行完毕后整理好游戏状态.
        这样可以避免监听器修改问题.
        """
        for listener in g.getListeners(event.player_id):
            ne = listener.listen(g, event)
            if ne is not None:
                for e in ne:
                    g = self._handle(g, e)
        ne = g.execute(event)
        if ne is not None:
            for e in ne:
                g = self._handle(g, e)
        if type(event) is not Over:
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