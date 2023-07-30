from __future__ import annotations

import sys

sys.path.append("..")
sys.path.append("../..")

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.core.GameInstance import GameInstance


from src.core.GameState import GameState, Item, Profile
from src.core.Event import *
from typing import List, Tuple, Mapping, Union, Any
from abc import ABCMeta, abstractmethod
from src.core.base import DiceInstance, DicePattern, Location


MAX_LISTEN_VAR = 5


class Listener(metaclass = ABCMeta):
    """
    实现take_listen方法. 如果中间出现用尽等情况, 只需要置alive=False.
    不要自己调用dicard,因为外部已经调用过了.
    
    注意usage=0并不意味alive=False. 如果你不清楚外部情况, 手动置alive=False总没错.
    """
    
    _vars = ['usage']
    def __init__(self) -> None:
        self.alive = True
        self.loc:Location = None
        self.usage = 0
        pass
    
    def record(self, name:str):
        """调用此方法来记录该类想要导出的成员变量. 
        尽管如此, 我们推荐手动配置_vars变量, 因为这样更快.
        
        如, self.a = 1
        self.record('a')
        
        之后调用export时会自动导出self.a. 装载时也会自动装载self.a
        
        注意必须传入字符串. 需在__init__中调用, 并且需要在最开头调用super().__init__().
        usage是默认字段, 总是第一个. 只要可能,都要优先利用usage字段.
        
        注:
        只有alive=True的监听器可能被导出.
        loc需要外部调用place()手动赋值.
        """
        assert type(name) == str
        self._vars.append(name)
        if len(self._vars) > MAX_LISTEN_VAR:
            raise "Too many variables! Try to remove constant like damage per hit or remove variables those only works in runtime."
    #def __getstate__(self):
    #    state = {
    #        'alive':True, 'loc':self.loc
    #    }
    #    for var in self._vars:
    #        state[var] = self.__dict__[var]
    #    return state
    def export(self)->Item:
        pass
    def restore(self, profile:Profile):
        for name, value in zip(self._vars, profile):
            setattr(self, name, value)
        pass
    def listen(self, g:"GameInstance", event)->Union[List[Event], None]:
        if self.alive and event.eid != -1:
            es = self.take_listen(g, event)
            es += self.discard(g,event)
            return es
        return []
    def place(self, loc:Location):
        self.loc = loc
    
    def discard(self, g, event):
        if self.alive == False:
            return [Discard(g.nexteid(), event.eid, event.player_id, self.loc)]
        return []
    
    @abstractmethod
    def take_listen(self, g:"GameInstance", event:Event)->List[Event]:
        pass
    
    
    
class Summoned(Listener):
    """
    Summoned是一类特殊的Listener, 它们仅有usage变量会被储存, 无法使用record方法.
    
    Summoned提供一个update方法, 传递一个usage变量, 该变量通常是init_usage, 即发生重名时外部传入的可用次数.
    对于某些Summon来说, 这里需要定义叠加规则. 对于大多数Summon而言, 这里取两者之高.
    
    注意, 快快缝补术不会调用update而是直接操控usage. 
    
    usage降至0却不弃置的召唤物(如莫娜E之类的)需要重写discard方法. discard即尝试discard当前召唤物, 若成功, 会返回一个Discard事件.
    Listener自带一个discard(若alive = False), 
    所以覆盖后可以令alive=False后调用super(Summoned, self).discard()来生成事件, 避免自己写错.
    注意super语法.
    
    除usage外, Summon存在以下**类**变量:
    
    init_usage:初始usage
    
    dvalue:该召唤物的(基础)伤害,相当于游戏中左下角的数字.
    dtype:该召唤物的伤害类型. 同DMGType.
    
    Summon存在一个默认take_listen方案, 即监听EndPhase事件并对敌方前台角色造成对应属性伤害.
    如果你的召唤物在伤害逻辑上与之一致, 只是需要监听别的事件,那么只需给dvalue,dtype赋值并调用super().take_listen()即可复用回合末监听
    
    如果你的召唤物存在群伤, 或者伤害数值不完全是dvalue等, 需要完全重写.
    """
    
    _vars = ['usage']
    dvalue = 1
    init_usage = 2
    dtype = DMGType.physical
    def __init__(self) -> None:
        super().__init__()
        self.usage = self.init_usage
    def record(self, name: str):
        raise NotImplementedError
    def discard(self, g, event):
        if self.usage <= 0:
            self.alive = False
        return super().discard(g, event)
    def take_listen(self, g: GameInstance, event: Event) -> List[Event]:
        if type(event) is not EndPhase:
            return []
        oppo = g.getactive(3 - self.loc.player_id)
        dmg = damage(self.loc,oppo, self.dtype, self.dvalue)
        d = RawDMG(g.nexteid(), event.eid, self.loc.player_id, [dmg])
        self.usage -= 1
        return [d]
    def update(self, usage):
        self.usage = max(self.usage, usage)
    
class Buff(Listener):
    """
    Buff是一个特殊的Listener分支. Buff拥有以下固有字段, 并且允许自定义_vars变量
    
    usage:同Listener
    is_shield: 是否是一个护盾状态
    
    init_usage:初始可用次数
    """
    init_usage = 0
    is_shield = False
    def __init__(self) -> None:
        super().__init__()
        self.usage = self.init_usage
    def update(self,usage):
        self.usage = max(self.usage, usage)
    

class CharBuff(Listener):
    """
    CharBuff和Buff非常类似.
    
    usage:同Listener
    
    类变量:
    is_shield: 是否是一个护盾状态
    init_usage:初始可用次数
    """
    init_usage = 0
    is_shield = False
    def __init__(self) -> None:
        super().__init__()
        self.usage = self.init_usage
    def update(self,usage):
        self.usage = max(self.usage, usage)

class Weapon(Listener):
    """
    weapontype:sword, claymore, catalyst, bow, polearm
    
    在装备武器时将检查该字段是否合法.
    """
    pass

class Artifact(Listener):
    pass

class Talent(Listener):
    pass

class ShieldBuff(Buff):
    """
    总是保护出战角色的护盾.
    
    修改init_usage来控制初始量. update默认不可叠加.
    
    若有特殊效应, 需要重写take_listen.
    """
    init_usage = 1
    is_shield = True
    def take_listen(self, g: GameInstance, event):
        if type(event) != DealDMG:
            return []
        active_loc = g.getactive(self.loc.player_id)
        #e_list = []
        for dmg in event.final_dmg_list:
            if dmg.dmgtype == DMGType.pierce:
                continue
            if dmg.target == active_loc:
                if dmg.dmgvalue < self.usage:
                    self.usage -= dmg.dmgvalue
                    dmg.dmgvalue = 0
                else:
                    dmg.dmgvalue -= self.usage
                    self.usage = 0
                    self.alive = False
                    break
        return []
    
class ShieldCharBuff(CharBuff):
    """
    仅保护所附属角色的护盾. update默认不可叠加
    
    通过init_usage控制.
    """
    
    init_usage = 2
    is_shield = True
    def take_listen(self, g: GameInstance, event):
        if type(event) != DealDMG:
            return []
        loc = Location(self.loc.player_id, self.loc.area, self.loc.index)
        #e_list = []
        for dmg in event.final_dmg_list:
            if dmg.dmgtype == DMGType.pierce:
                continue
            if dmg.target == loc:
                if dmg.dmgvalue < self.usage:
                    self.usage -= dmg.dmgvalue
                    dmg.dmgvalue = 0
                else:
                    dmg.dmgvalue -= self.usage
                    self.usage = 0
                    self.alive = False
                    break
        return []

class CrystallizeShield(ShieldBuff):
    is_shield = True
    init_usage = 1
    def update(self, usage):
        self.usage += usage
        self.usage = min(2, self.usage)
    
    
#TODO:
class CatalyzingField(Buff):
    init_usage = 2
    def take_listen(self, g: GameInstance, event):
        if type(event) == DMG or type(event) == Reaction:
            for dmg in event.dmg_list:
                if dmg.attacker.player_id == self.loc.player_id:
                    if dmg.dmgtype == DMGType.electro or dmg.dmgtype == DMGType.dendro:
                        dmg.dmgvalue += 1
                        self.usage -= 1
                        if self.usage <= 0:
                            self.alive = False
                            break
        return []

class DendroCore(Buff):
    init_usage = 1
    def take_listen(self, g: GameInstance, event):
        if type(event) == DMG or type(event) == Reaction:
            for dmg in event.dmg_list:
                if dmg.attacker.player_id == self.loc.player_id:
                    if dmg.dmgtype == DMGType.electro or dmg.dmgtype == DMGType.pyro:
                        dmg.dmgvalue += 2
                        self.usage -= 1
                        if self.usage <= 0:
                            self.alive = False
                            break
        return []

class BurningFlame(Summoned):
    dtype = DMGType.pyro
    dvalue = 1