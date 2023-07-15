import sys
sys.path.extend(['..','../..'])

from dataclasses import dataclass
from src.core.base import Location, DiceInstance, DicePattern
from enum import Enum
from typing import List, Tuple, Dict, Callable, Mapping, Any


# +
@dataclass
class Instruction:
    player_id:int
    dice_pattern:DicePattern#此值保存最初的pattern. 它将随后被传给event
    real_dice_pattern:DicePattern##此值是预计算减费后的
    dice_instance:DiceInstance

    @property
    def player_pattern(self):
        return self.dice_instance
    @player_pattern.setter
    def _(self,value):
        self.dice_instance = value

@dataclass
class EndRound(Instruction):
    pass
#ER = EndRound(1,2)

@dataclass
class Switch(Instruction):
    direction:int #-1,1
    ##主动切人.
    ##1 black
    
@dataclass
class UseKit(Instruction):
    kit:str #na, skill, burst, sp1, sp2
    ##作为Instruction时, 必然是active角色才能使用技能, 因此不需要char_loc
    ##不过Event端则不一样(可能出牌也是战斗行动).

@dataclass
class PlayCard(Instruction):
    offset:int##No. offset in hand
    targets:List[Location]

@dataclass 
class Tuning(Instruction):
    card_offset:int
    dice_color:str##转换前的颜色.
    ##将转换前的颜色转换成出战角色颜色.
    

"""
以下是非标准动作. 这些动作要么很少见(换牌), 要么涉及到随机(骰)
"""

@dataclass
class Roll(Instruction):
    rolled:DiceInstance##哪些骰子被重骰

@dataclass
class ExchangeCard(Instruction):
    swapout:List[int]