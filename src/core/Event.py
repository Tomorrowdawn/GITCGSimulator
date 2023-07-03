from dataclasses import dataclass, replace
from enum import Enum
from typing import List, Tuple, Dict, Callable, Mapping, Any
from base import Location, DiceInstance, DicePattern

@dataclass
class Event:
    eid:int
    source_id:int
    player_id:int###用于获取监听器顺序, 也可以用来表明是谁引发的事件

@dataclass
class Over(Event):
    ##它的source_id就是结束的事件.
    pass
    
@dataclass
class EndRound(Event):
    pass
    
#ER = EndRound(1,2)
@dataclass
class StartPhase(Event):
    pass

@dataclass
class EndPhase(Event):
    pass

@dataclass
class Switch(Event):
    char_loc:Location##before
    direct:int #-1,1
    dice_cost:DiceInstance = None
    ##注意Switch不一定能执行成功.
    ##例如凯亚大招这种监听器, 在听到Switch时就要记录一下active_loc
    ##听到Over(Switch)时对比一下. 如果没变, 就说明切换失败了, 不能响应.
    ##主动切人和被动切人: 如果source_id = -1,就是主动. 否则就是被动.
@dataclass
class Death(Event):
    char_loc:Location

@dataclass 
class SwapMove(Event):
    now_mover:int## i.e. player_id
    ifswap:bool = True##True or False. default = True
    
@dataclass
class GenerateDice(Event):
    dice_instance:dict
    ###dice_instance该实例就是最终结果.
    #例如卯师傅等随机骰子卡, 在外部确定后传过来即可.
    
@dataclass
class DicePreCal(Event):
    event_instance:Any##实际上只是其中几个, 例如切人Switch. 
    ## 这个地方会初始化一个无效事件(event_id=-1). 但是必要的参数仍需要添加(例如playcard的offset(否则监听器无法确定是哪张卡))
    ##只是为了type能够正确执行(因为传类名会出错)
    dice_pattern:dict
    ##该事件发出时, 骰子消耗还未执行
    ##监听器监听此事件, 不修改自己的状态, 但是修改dice_pattern.
    ##某些卡牌， 例如雷楔，天赋卡，同时会产生一个战斗行动
    ## 因此,监听器如果监听的对象是Kit, 除UseKit外,需要额外监听PlayCard.
    ## 雷楔的计算过程:
    ## 首先产生PlayCard. 随后监听器调用fetch获取卡牌, 
    ## 然后调用卡牌的DicePreCal_type方法, 将获得dict['UseKit'] = keqing_loc
    ## 此时监听器就会比对loc是否正确(例如圣遗物), 是否使用过(艾琳)等.
    ## TODO: 之后将写一个装饰器, 其中提供参数是否监听卡牌.
    
@dataclass
class UseKit(Event):
    cur_char:Location
    Kit_Type:str##na,skill,burst
    Kit_func:Any
    ##直接将角色实例的方法传入
    ##Kit_func(source_id, game)
    dice_cost:DiceInstance = None

class DMGType(Enum):
    pyro = 0
    hydro = 1
    dendro = 2
    cryo = 3
    geo = 4
    anemo = 5
    electro = 6
    physical = 7
    pierce = 8

@dataclass
class damage:
    attacker:Location
    target:Location
    dmgtype:DMGType
    dmgvalue:int
    
@dataclass
class DMGTypeCheck(Event):
    dmg_list:List[damage]
    
@dataclass
class DMG(Event):
    #dmg_list: 一系列同时发生的伤害
    #一般来说, 伤害都只有一个attacker. 处理伤害时要自动对齐伤害来源
    dmg_list:List[damage]
    def merge(self, another):
        self.dmg_list.extend(another.dmg_list)
    ##DMG被execute则转换为DealDMG
    ##dvalue < 0的事件需要忽略伤害效应!!
    ##所有加伤事件也应该忽略掉dvalue<0的事件!
    def real_dmg(self):
        return [dmg for dmg in self.dmg_list if dmg.dmgvalue >= 0]

@dataclass
class DealDMG(Event):
    final_dmg_list:List[damage]
    ## 此事件表示所有加伤都计算完毕. 莫娜泡影属于例外.
    ##所有护盾都监听这个事件.
    ## 莫娜泡影监听这个事件.
    
@dataclass
class dose:
    target:Location
    heal_points:int
@dataclass
class Heal(Event):
    doses:List[dose]
    
@dataclass
class Reaction(Event):
    location:Location##
    reaction_name:str
    trigger_element:DMGType
    triggered_element:DMGType
    
@dataclass
class AddCard(Event):
    player_id:int
    card_cls:Any
    ###目前应该只有刻晴雷楔.
@dataclass
class PlayCard(Event):
    player_id:int
    offset:int##No. offset of hand
    targets:List[Location]
    dice_cost:DiceInstance = None
    
@dataclass
class Tuning(Event):
    player_id:int
    card_offset:int
    dice_color:str##转换前的颜色
    ###该事件不会产生DiceInstance.直接被执行.
    ##先消耗掉一枚dice_color对应的骰子, 再产生一枚和出战角色一样的.

@dataclass
class DrawCard(Event):
    player_id:int
    number:int
    Cardfilter:Any##接收一张卡牌, 返回True or false. 只抽取特定的卡牌
    #None表示无限制

##以下几个类的提醒: 如果有效应修改了原来的召唤物/状态, 则先摧毁后产生
##若没有修改, 则刷新. 所以execute里面应该是先查名字, 查到了再看具体类型.

#这里标记用Any纯粹是为了避免循环依赖. 应该是Listener.
##以下所有创建类事件的初始化都是一样的
##XXX(loc, EM,game)
@dataclass
class Summon(Event):
    player_id:int##which side's summon area
    summoned:Any

@dataclass
class CreateBuff(Event):
    player_id:int
    buff:Any

@dataclass
class CreateCharBuff(Event):
    char_loc:Location
    char_buff:Any

@dataclass
class CreateSupport(Event):
    player_id:int
    support:Any

@dataclass
class Equip(Event):
    char_loc:Location
    equipment:Any

@dataclass
class CreateHandListener(Event):
    player_id:int
    handlistener:Any
    
@dataclass
class Discard(Event):
    ##执行Discard以删除监听器
    ##area需要自行维护alive列表(增删改查的时候. listen已经进行了前置检查)
    discard_loc:Location
    ## discard需要检查一下是否为frozenlistener. 如果是,还需要修改char那边的frozen.
    
@dataclass
class ChargeEnergy(Event):
    """energy_slots>0,充能. e_s<0,消耗充能(白垩)"""
    loc:Location
    energy_slots:int#充能数