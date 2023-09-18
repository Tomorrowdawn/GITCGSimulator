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
    def empty(self)->bool:
        return self.omni | self.pyro | self.cryo | self.hydro | self.electro | self.dendro | self.anemo | self.geo

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
    omni:int = 0
    def to_dict(self):
        return asdict(self)

def get_oppoid(player_id):
    return 3 - player_id

def samecharcheck(loc1:Location, loc2:Location):
    if loc1.player_id != loc2.player_id:
        return False
    if loc1.area != 'Char' or loc2.area != 'Char':
        return False
    if loc1.index != loc2.index:
        return False
    return True