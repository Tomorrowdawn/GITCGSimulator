from dataclasses import dataclass, asdict
@dataclass
class Location:
    player_id:int
    area:str##Char, Support, Summon, TeamBuff, Hand
    index:int
    
    ###仅用于装备/角色状态定位
    subarea:str = '' ### empty if you only need character. else it's weapon/artifact/talent/buff
    offset:int = 0 ##only available if subarea=buff.
    
@dataclass
class DiceInstance:
    omni:int = 0
    pyro:int = 0
    cryo:int = 0
    hydro:int = 0
    electro:int = 0
    dendro:int = 0
    anemo:int = 0
    geo:int = 0
    
    def to_dict(self):
        return asdict(self)

@dataclass
class DicePattern:
    pyro:int = 0
    cryo:int = 0
    hydro:int = 0
    electro:int = 0
    dendro:int = 0
    anemo:int = 0
    geo:int = 0
    black:int = 0
    white:int = 0
    def to_dict(self):
        return asdict(self)
