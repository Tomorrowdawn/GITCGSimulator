from dataclasses import dataclass, replace

@dataclass
class Event:
    eid:int
    source_id:int
    player_id:int###用于获取监听器顺序
