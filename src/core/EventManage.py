from __future__ import annotations
"""
本代码实现事件处理框架以及事件执行(分派)函数.
"""

from src.core.Event import Event, Over, Death
from src.core.Listener import Listener
from src.core.GameState import GameState
from src.core.error import CallBackError

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.core.GameInstance import GameInstance
import pickle

def picklecopy(obj):
    return pickle.loads(pickle.dumps(obj))

class EventHub:
    def __init__(self,q = []) -> None:
        self.q = q
        pass
    def process(self, g:GameInstance, event:Event, callback)->None:
        if event.eid == -1:
            return
        self.q = [event]
        self.checkout(g, callback)
    def checkout(self, g:GameInstance, callback = None):
        #self.q.append(event)
        while len(self.q) > 0:
            event = self.q.pop(0)
            if event.eid != -1:
                self.q = self._expand(g,event,callback) + self.q
    def _expand(self, g, event, callback):
        queue = []
        for listener in g.getListeners(event.player_id):
            ne = listener.listen(g, event)
            queue.extend(ne)
        ne = g._execute(event)
        queue.extend(ne)
        if g.history['phase'] in ('deathswitch','roll','firstfive') and (
            isinstance(event, Death) 
        ):
            if callback is not None:
                if type(event) is not Over:
                    q = [Over(g.nexteid(),event.eid, event.player_id, event)] + self.q
                else:
                    q = self.q
                e = callback(g, event, picklecopy(queue), picklecopy(q))
                queue.append(e)
            else:
                raise CallBackError("no callback is provided however it's phase {}".format(g.history['phase']))
        if type(event) is not Over:
            queue.append(Over(g.nexteid(),event.eid, event.player_id, event))
        return queue
                    
        
# class EventHub:
#     """处理事件流程"""
#     def __init__(self) -> None:
#         self.cache = []
#     def process(self, g:GameInstance, event:Event, callback)->None:
#         self._handle(g,event, callback)
#         g.rebuild()
#     def _handle(self, g:GameInstance, event:Event, callback = None)->None:
#         """强制性只执行一个事件, 每次执行完毕后整理好游戏状态.
#         这样可以避免监听器修改问题.
#         """
        
#         if event.eid == -1:
#             return 
#         #print("eventhub event = ", event)
#         for listener in g.getListeners(event.player_id):
#             ne = listener.listen(g, event)
#             for e in ne:
#                 self._handle(g, e, callback)
#         ne = g._execute(event)##执行Over是有意义的.
#         if g.history['phase'] in ('deathswitch','roll','firstfive'):
#             if callback is not None:
#                 e = callback(g, event)
#                 self._handle(g, e, callback)
#             else:
#                 raise CallBackError("no callback is provided however it's phase {}".format(g.history['phase']))
#         for e in ne:
#             self._handle(g, e, callback)
#         if event.eid != -1 and type(event) is not Over:
#             nid = g.nexteid()
#             self._handle(g, Over(nid, event.eid, event.player_id, event), callback)
#         ###for listener in L:
#         ###      if listener.listen(event) is not None:
#         ###          handle(new events by order)
#         ###execute event.
#         ###if new events
#         ### handle(new events)
#         ###if event is not Over:
#         ###NGS = handle(Over(event))
#         ###return new GameState
#         pass
#     pass