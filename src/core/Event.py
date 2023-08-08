from dataclasses import dataclass, replace
from enum import Enum, IntEnum
from typing import List, Tuple, Dict, Callable, Mapping, Any
from src.core.base import Location, DiceInstance, DicePattern

@dataclass
class Event:
    eid:int
    source_id:int
    player_id:int###用于获取监听器顺序, 也可以用来表明是谁引发的事件

@dataclass
class Over(Event):
    ##它的source_id就是结束的事件.
    overed:Event = None
    pass
    
@dataclass
class GameStart(Event):
    pass

@dataclass
class EndRound(Event):
    pass###注意维护history,比如plunge等.
    
#ER = EndRound(1,2)
@dataclass
class StartPhase(Event):
    pass

@dataclass
class EndPhase(Event):
    pass###注意这里的player_id应该和下一轮的mover(先结束方)对应.

@dataclass
class RollPhase(Event):
    ###rollcallback
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
    succeed:bool = False
    
@dataclass
class Death(Event):
    char_loc:Location##如果是前台死了,要触发deathswitch阶段.

@dataclass 
class SwapMove(Event):
    now_mover:int## i.e. player_id
    ifswap:bool = True##True or False. default = True
    
@dataclass
class GenerateDice(Event):
    dice_pattern:DicePattern
    ###black表示杂骰(不含omni). 元素对应元素骰
    ##white表示纯随机.
    
@dataclass
class Roll(Event):
    ###投掷结果.
    ###3费圣遗物,群玉阁修改enforce_dice
    dice_instance:DiceInstance
    enforce_dice:DiceInstance = DiceInstance()
    ##execute在汇总后用enforce_dice替换掉dice_instance中的部分.
    ##Roll也会修改mover, 但只是单纯因为无法做到同时掷骰而已, 不会触发SwapMove.
    
    
@dataclass
class DicePreCal(Event):
    event_instance:Any##实际上只是其中几个, 例如切人Switch. 
    ## 这个地方会初始化一个无效事件(event_id=-1). 但是必要的参数仍需要添加(例如playcard的offset(否则监听器无法确定是哪张卡))
    ##只是为了type能够正确执行(因为传类名会出错)
    dice_pattern:DicePattern
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
    kit:str##na,skill,burst, sp1, sp2
    kit_type:str##na,skill,burst
    dice_cost:DiceInstance = None

class DMGType(IntEnum):
    physical = 0
    pyro = 1
    cryo = 2
    electro = 3
    hydro = 4
    dendro = 5
    crydendro = 6
    anemo = 7
    geo = 8
    #physical = 9
    pierce = 9

@dataclass
class damage:
    attacker:Location
    target:Location
    dmgtype:DMGType
    dmgvalue:int
    reason:str = 'self'

@dataclass
class DMGTypeCheck(Event):
    dmg_list:List[damage]
    
RawDMG = DMGTypeCheck ##别名
    
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
    location:Location
    ##在哪个地方发生了反应, 
    # 这必然是一个角色的位置. 
    # 注意该location可能与player_id不同, 
    # 以location为准, player_id仅表示这是谁触发的
    reaction_name:str
    trigger_element:DMGType###先手元素
    triggered_element:DMGType##后手元素
    dmg_list:List[damage]
    ###默认dmg_list是已经处理好增伤的列表(主要是因为扩散可能导致相当复杂的结算,需要当场算出来).
    ###EventExecute需要处理的是副作用(激化领域, 结晶盾, etc)
    
@dataclass
class AddCard(Event):
    card_cls:Any
    ###目前应该只有刻晴雷楔.
@dataclass
class PlayCard(Event):
    offset:int##No. offset of hand
    targets:List[Location]
    dice_cost:DiceInstance = None
    
@dataclass
class Tuning(Event):
    card_offset:int
    dice_color:str##转换前的颜色
    ###该事件不会产生DiceInstance.直接被执行.
    ##先消耗掉一枚dice_color对应的骰子, 再产生一枚和出战角色一样的.

@dataclass
class DrawCard(Event):
    number:int
    Cardfilter:Any = None##接收一张卡牌, 返回True or false. 只抽取特定的卡牌
    #None表示无限制
    
@dataclass
class ExchangeCard(Event):
    indices:list##list[int],卡牌下标. 将这些卡牌放回去然后抽取等量卡牌.


##以下几个类的提醒: 如果有效应修改了原来的召唤物/状态, 则先摧毁后产生
##若没有修改, 则刷新. 所以execute里面应该是先查名字, 查到了再看具体类型.

#这里标记用Any纯粹是为了避免循环依赖. 应该是Listener.
##以下所有创建类事件的初始化都是一样的
##XXX()
###XXX.place(loc) loc由外部计算得出.
### 内部传递的都是类名. 因为事件不需要pickle,所以传类名也没关系.
@dataclass
class Summon(Event):
   ##which side's summon area
    target_player_id:int
    summoned:Any

@dataclass
class CreateBuff(Event):
    target_player_id:int
    buff:Any

@dataclass
class CreateCharBuff(Event):
    char_loc:Location
    char_buff:Any

@dataclass
class CreateSupport(Event):
    target_player_id:int
    support:Any

@dataclass
class Equip(Event):
    char_loc:Location
    equipment:Any###equipment的类变量中包含了具体是天赋,武器还是圣遗物

@dataclass
class CreateHandListener(Event):
    target_player_id:int
    handlistener:Any
    
@dataclass
class Discard(Event):
    ##执行Discard以删除监听器
    ##area需要自行维护alive列表(增删改查的时候. listen已经进行了前置检查)
    discard_loc:Location
    discard_name:str
    ## discard需要检查一下是否为frozenlistener. 如果是,还需要修改char那边的frozen.
    
@dataclass
class ChargeEnergy(Event):
    """energy_slots>0,充能. e_s<0,消耗充能(白垩)"""
    loc:Location
    energy_slots:int#充能/扣能