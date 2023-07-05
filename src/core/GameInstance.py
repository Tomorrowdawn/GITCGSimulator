import sys
sys.path.append("..")
sys.path.append("../..")

from functools import singledispatchmethod
from src.core.GameState import GameState, Profile, Item, PlayerState

from dataclasses import dataclass, asdict
from typing import Tuple, List, Any, Mapping, Union
from copy import deepcopy
from abc import ABCMeta, abstractmethod
from src.core.base import DiceInstance, DicePattern, Location
from src.card.card import Card, Deck, Hand
from src.character.character import Character
from src.character.utils import name2char
from src.core.Event import *
from src.core.Listener import Listener
from src.core.GameState import Aura, AuraList
from src.core.EventManage import EventHub
import src.core.Instruction as Ins
import random

dice_pattern_list = list(DicePattern().to_dict().keys())
dice_ins_list = list(DiceInstance().to_dict().keys())

class DicePool:
    def __init__(self) -> None:
        self.dice = DiceInstance()
    def checkPattern(self, dice_pattern:DicePattern)->bool:
        """验证当前骰子是否支持该Pattern"""
        n = 0
        for k,v in dice_pattern.to_dict():
            n += v
        dn = 0
        for k, v in self.dice.to_dict():
            dn += v
        if n > dn:
            return False
        return True##TODO: 目前全是万能(V1)
    def _add(self, dices:List[str]):
        d = self.dice.to_dict()
        for die in dices:
            d[die] += 1
        self.dice = DiceInstance(**d)
    def set(self, di):
        self.dice = di
    def addDice(self, dice_pattern:DicePattern):
        """
        根据dice_pattern生成新的骰子,加入骰池
        
        dice_pattern: 黑表示三个不同的随机元素骰. 白为直接投掷N个八面骰. 其余同常规定义
        注:这里的dice_pattern不需要完整版本(即,可以省略个数为0的骰子)
        
        开局骰8个骰子的时候可以用white=8控制.
        """
        dp = dice_pattern.to_dict()
        pure_element = ['pyro','electro','geo','anemo','dendro','hydro','cryo']
        for element, num in dp.items():
            if element == 'black':
                generated = random.sample(pure_element, k = num)
                self._add(generated)
            elif element == 'omni':
                self._add([element] * num)
            elif element in dice_ins_list:
                self._add([element] * num)
            elif element == 'white':
                generated = random.choices(dice_ins_list,k = num)
                self._add(generated)
            else:
                raise "Unknown dice type"
    def consume(self, dice_instance:DiceInstance):
        di = dice_instance.to_dict()
        n = 0
        for k , v in di.items():
            n += v
        self.dice.omni -= n
        if self.dice.omni < 0:
            raise "Not Enough Dices"
        pass
    pass


class PlayerInstance:
    def __init___(self, g:PlayerState):
        player_id = g.history['player_id']
        self.deck = Deck(g.deck)
        self.hand = Hand(g.hand)
        self.char:List[Character] = [name2char(char).restore(profile) for char, profile in g.char]
        for i, c in enumerate(self.char):
            loc = Location(player_id, 'Char',i)
            c:Character
            c.place(loc)
        self.dice = DicePool(g.dice)
        self.history = g.history
        #self.teambuff
        #self.support
        #self.summon
        ##TODO:
        pass
    def charView(self, active)->List[Character]:
        views = []
        for c in self.char[active:]:
            views.append(c)
        views.extend(self.char[:active])
        return views
    def rmListener(self, loc:Location):
        pass
    def getListeners(self)->List[Listener]:
        ls = list()
        active = self.history['active']
        char = self.charView(active)
        for c in char:
            ls.extend(c.getListeners())
        ##TODO:还有其他区域的监听器.
        return ls
    def getAura(self)->List[Aura]:
        auras = list()
        for c in self.char:
            if not c.died():
                auras.append(c.aura)
            else:
                auras.append(Aura.died)
        return auras
    def get(self, loc:Location)->Union[Character, Listener]:
        area = loc.area
        if area != 'Char':
            area = area.lower()
            Area = self.__dict__[area]
            return Area[loc.index]
        else:
            Area = self.char
            char = Area[loc.index]
            if loc.subarea == '':
                return char
            elif loc.subarea == 'talent':
                return char.talent
            elif loc.subarea == 'weapon':
                return char.weapon
            elif loc.subarea == 'artifact':
                return char.artifact
            else:
                buff = char.buff
                return buff[loc.offset]
    def export(self)->PlayerState:
        pass
class GameInstance:
    """提供方便的接口修改游戏状态, 执行事件,并可以导出GameState"""
    def __init__(self,g:GameState) -> None:
        #self.g = g.clone()
        #不能直接存, 因为GameInstance是要修改状态的, 而GameState是只读的.
        ## 需要读成GameInstance的内部格式.
        self.maxid = 0
        self.thinking = False
        self.dice1 = DiceInstance()
        self.dice2 = DiceInstance()
        if g is None:
            return
        """TODO:激活所有类"""
        
        """
        包括Deck,Hand, 全部要读入对应类中.
        """
        self.p1 = PlayerInstance(g.players[0])
        self.p2 = PlayerInstance(g.players[1])
        self.history :GameState.History = g.history
    
    def proceed(self, ins):
        eh = EventHub()
        ##TODO:
        events = self.translate(ins)
        for e in events:
            eh.process(self, ins)
    
    def think(self, set1,set2):
        """
        设置为thinking模式. 此模式下, Roll,DrawCard事件会失效. 
        双方的手牌固定, 骰子固定.
        set:(hand, diceInstance). set1表示player1, set2表示player2
        hand需要你自己预测. 谨记, hand数量会影响打出&调和选择分支数量, 每一张卡都要仔细斟酌, 分支+1对于搜索的影响都是毁灭性的(而新增一张卡会导致分支+2).
        diceInstance的常见设定为对方6万能2杂, 而自己是4万能. 
        
        一般要悲观估计. thinking模式下, 调和牌(小派蒙,凝光,图书馆)会失效. 取而代之, 如果你的手牌中有这些牌, 你可以将其去掉, 然后调高自己的掷骰期望.
        如果你的hand远低于实际手牌数, 也可以调高Dice期望(视作你调和了其他牌).

        dicePattern会替换双方的掷骰操作结果.
        """
        self.thinking = True
        hand, dice = set1
        self.p1.dice.set(dice)
        self.p1.hand = Hand(hand)
        
        hand,dice = set2
        self.p2.dice.set(dice)
        self.p2.hand = Hand(hand)
        pass
    
    def rebuild(self)->None:
        """检查并整理好游戏状态
        
        ~~检查所有监听器并删掉alive=False~~
        现在监听器会在Discard后立刻被移除. 此函数保留为以后可能所用.
        
        注意, 监听器alive只有在discard事件被执行后才能被更改.
        
        此函数不触发事件. 
        """
        pass
    def getListeners(self, player_id)->List[Listener]:
        if player_id == 1:
            return self.p1.getListeners() + self.p2.getListeners()
        else:
            return self.p2.getListeners() + self.p1.getListeners()
    def getAura(self, player_id)->List[Aura]:
        if player_id == 1:
            return self.p1.getAura()
        else:
            return self.p2.getAura()
    def export(self)->GameState:
        #return self.g.clone()
        ##需要将各个监听器的数据统一导出而非clone.
        ##TODO:
        g = GameState()
        p1 = self.p1.export()
        p2 = self.p2.export()
        g.players.append(p1)
        g.players.append(p2)
        g.history = deepcopy(self.history)
        return g
    def get(self, loc:Location):
        if loc.player_id == 1:
            pds = self.p1
        else:
            pds = self.p2
        return pds.get(loc)
    def nexteid(self)->int:
        self.maxid += 1
        return self.maxid
    def _getpds(self, player_id):
        return self.p1 if player_id == 1 else self.p2
    def getactive(self,player_id)->Location:
        if player_id == 1:
            pds = self.p1
        else:
            pds = self.p2
        
        active = pds.history['active']
        loc = Location(player_id, 'Char', active)
        
        return loc
    def getstandby(self, player_id)->List[Location]:
        pds = self._getpds(player_id)
        ##TODO:
        pass
    def make_damage(self, player_id, target:Union[Location,str], 
                    dvalue, dtype, source = 'active')->List[damage]:
        """
        target,source:定位符. 可以使用active or standby,也可以使用Location.
        (使用active或standby可能不足以定位)
        
        此接口返回一个damage列表. 通常情况下列表长1, 如果使用standby且后台两人存活,那么长2.
        """
        
        #damage()
        if source != 'active':
            assert type(source) == Location
        else:
            source = self.getactive(player_id)
        if target == 'active':
            target = self.getactive(3 - player_id)
            return [damage(source,target,dtype,dvalue)]
        elif target == 'standby':
            targets = self.getstandby(3-player_id)
            return [damage(source,tar,dtype,dvalue) for tar in targets]
        else:
            return [damage(source,target,dtype,dvalue)]  
    @singledispatchmethod
    def translate(self, ins)->List[Event]:
        pass
    
    @translate.register
    def usekit(self, ins:Ins.UseKit):
        active_loc = self.getactive(ins.player_id)
        active = self.get(active_loc)
        active:Character
        t = active.skill_type[ins.kit]
        return UseKit(self.nexteid(), -1, ins.player_id, active_loc, ins.kit, t, ins.dice_instance)
    @property
    def mover(self):
        return self.history['mover']
    
    def _execute(self, event:Event):
        if event.eid == -1:
            return []
        else:
            return self.execute(event)
    
    @singledispatchmethod
    def execute(self, event)->Union[List[Event],None]:
        ##这里使用分派.
        pass
    
    @execute.register
    def dmgtypecheck(self, event:DMGTypeCheck):
        ###这里检查是否会发生反应并发射反应事件（如果有）。
        pass
    
    @execute.register
    def usekit(self, event:UseKit):
        active = self.get(event.cur_char)
        active_loc = event.cur_char
        source = event.eid
        if event.kit not in active.no_charge:
            CE = ChargeEnergy(self.nexteid(), source, event.player_id, active_loc, 1)
        SM = SwapMove(self.nexteid(), event.eid, event.player_id, self.mover)
        kit = event.kit
        cast = active.__dict__[kit]##释放技能
        new_events = cast(self)
        return new_events + [CE, SM]
    
    @execute.register
    def charge(self, event:ChargeEnergy):
        char = self.get(event.loc)
        char:Character
        char.charge(event.energy_slots, event.eid, self)
        return []
    
    @execute.register
    def swapmove(self, event:SwapMove):
        if event.ifswap:
            self.history['mover'] = 3 - self.history['mover']
        return []
    