import sys
sys.path.append("..")
sys.path.append("../..")

from functools import singledispatchmethod
from src.core.GameState import GameState, Profile, Item, PlayerState

from typing import Tuple, List, Any, Mapping, Union
from src.core.base import DiceInstance, DicePattern, Location, get_oppoid
from src.card.card import Card, Deck, Hand
from src.character.character import Character
from src.character.utils import name2char
from src.core.Event import *
from src.core.Listener import Listener
from src.core.GameState import Aura, AuraList
from src.core.EventManage import EventHub
from src.core.Listener import Summon,Buff

import src.core.Instruction as Ins
import random
import pickle

def picklecopy(obj):
    return pickle.loads(pickle.dumps(obj))

dice_pattern_list = list(DicePattern().to_dict().keys())
dice_ins_list = list(DiceInstance().to_dict().keys())

class DicePool:
    def __init__(self, dice = None) -> None:
        self.dice = DiceInstance()
        if dice != None:
            self.dice = dice
    def num(self)->int:
        dn = 0
        for k, v in self.dice.to_dict().items():
            dn += v
        return dn
    def checkPattern(self, dice_pattern:DicePattern)->bool:
        """验证当前骰子是否支持该Pattern"""
        n = 0
        for k,v in dice_pattern.to_dict().items():
            n += v
        dn = 0
        for k, v in self.dice.to_dict().items():
            dn += v
        if n > dn:
            return False
        return True##TODO: 目前全是万能(V1)
    def _add(self, dices:List[str]):
        d = self.dice.to_dict()
        for die in dices:
            d[die] += 1
        self.dice = DiceInstance(**d)
    def addDiceInstance(self, dice_instance:DiceInstance):
        for k, v in dice_instance.to_dict().items():
            self.dice[k] += v
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
        if dice_instance is None:
            return
        di = dice_instance.to_dict()
        n = 0
        for k , v in di.items():
            n += v
        self.dice.omni -= n
        if self.dice.omni < 0:
            raise Exception("Not Enough Dices")
        pass
    pass

def loadchar(name, profile):
    c = name2char(name)
    c.restore(profile)
    return c

class PlayerInstance:
    def __init__(self, g:PlayerState):
        if g is None:
            return
        player_id = g.history['player_id']
        self.deck = Deck(g.deck)
        self.hand = Hand(g.hand)
        #print("chars = ",g.char)
        self.char:List[Character] = [loadchar(char, profile) for char, profile in g.char]
        for i, c in enumerate(self.char):
           # print("char = ",c)
            loc = Location(player_id, 'Char',i)
            c.place(loc)
        self.dice = DicePool(g.dice)
        self.history = g.history
        self.teambuff = []
        #self.support = []
        self.summon:List[Summon] = []
        ##TODO: 别忘了place
        pass
    def charView(self, active:int)->List[Character]:
        """
        active是index.
        """
        views = []
        for c in self.char[active:]:
            views.append(c)
        views.extend(self.char[:active])
        return views
    def rmListener(self, loc:Location):
        ##TODO:
        pass
    def getListeners(self)->List[Listener]:
        ls = list()
        active = self.history['active']
        char = self.charView(active)
        for c in char:
            if c.hp > 0:
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
    def setAura(self, new_aura):
        for aura, c in zip(new_aura,self.char):
            c.aura = aura
    def getalives(self)->List[Location]:
        locs = []
        for c in self.char:
            if c.hp > 0:
                locs.append(c.loc)
        return locs
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
    def startphase_reset(self):
        self.history['dieThisRound'] = False
        self.history['endround'] = False
        self.history['plunge'] = False
        for c in self.char:
            if not c.died():
                c.startphase_reset()
    def export(self)->PlayerState:
        p = PlayerState()
        p.deck = self.deck.export()
        p.hand = self.hand.export()
        p.char = [c.export() for c in self.char]
        p.dice = picklecopy(self.dice)
        p.history = picklecopy(self.history)
        ##TODO:
        return p
    def clone(self):
        p = PlayerInstance(None)
        p.deck = picklecopy(self.deck)
        p.hand = picklecopy(self.hand)
        p.char = picklecopy(self.char)
        p.dice = picklecopy(self.dice)
        p.history = picklecopy(self.history)
        ##TODO:
        return p
class GameInstance:
    """提供方便的接口修改游戏状态, 执行事件,并可以导出GameState"""
    def __init__(self,g:GameState) -> None:
        #self.g = g.clone()
        #不能直接存, 因为GameInstance是要修改状态的, 而GameState是只读的.
        ## 需要读成GameInstance的内部格式.
        self.maxid = 0
        self.thinker = -1
        self.estimator = None
        if g is None:
            return
        """
        包括Deck,Hand, 全部要读入对应类中.
        """
       # print(g.players[0])
        self.p1 = PlayerInstance(g.players[0])
        self.p2 = PlayerInstance(g.players[1])
        self.history :GameState.History = g.history
    
    def proceed(self, ins, new_instance = False, callback = None):
        """
        new_instance:若为True, 则返回一个GameInstance的深拷贝. 
        这个选项一般在AI搜索中开启, 正式对局中没有必要拷贝对局.
        
        callback:接收GameInstance和event参数(注意顺序)的函数, 返回一个事件.
        一般callback下分别有两个玩家自己的策略, 顶级函数根据event.player_id分发事件.
        
        callback的常用参考是history['phase']变量.
        
        roll:期待一个Roll事件
        firstfive:期待一个ExchangeCard事件.
        deathswitch:期待一个Switch事件.
        """
        eh = EventHub()
        self.maxid = 0
        ##TODO:
        events = self.translate(ins)
        for e in events:
            eh.process(self, e, callback)
        if new_instance:
            return self.clone()
    def choose_active(self, player_id, active):
        pds = self._getpds(player_id)
        assert active >= 0 and active <= 2
        pds.history['active'] = active
    def _issue(self, event, callback):
        eh = EventHub()
        eh.process(self, event, callback)
    def think(self,oppo_hand:list, player_id, estimator = None):
        """
        设置为thinking模式. 此模式下, 我方及对方的roll, 对方的drawcard事件会直接失效.
        roll,generatedice等事件将会调用estimator回调函数. 对方的drawcard会失效. 我方的drawcard正常执行(配合外部的蒙特卡洛方法)
        
        estimator(event, g), 返回一个DiceInstance用于消除随机性.
        
        双方的手牌固定, 骰子固定.
        set:(hand, diceInstance). set1表示player1, set2表示player2
        hand需要你自己预测. 谨记, hand数量会影响打出&调和选择分支数量, 每一张卡都要仔细斟酌, 分支+1对于搜索的影响都是毁灭性的(而新增一张卡会导致分支+2).
        diceInstance的常见设定为对方6万能2杂, 而自己是4万能. 
        
        一般要悲观估计. thinking模式下, 调和牌(小派蒙,凝光,图书馆)会失效. 取而代之, 如果你的手牌中有这些牌, 你可以将其去掉, 然后调高自己的掷骰期望.
        如果你的hand远低于实际手牌数, 也可以调高Dice期望(视作你调和了其他牌).

        dicePattern会替换双方的掷骰操作结果.
        """
        self.thinker = player_id
        self.estimator = estimator
        self.p2.hand = Hand(oppo_hand)
        
        ###TODO: 修改为对Monte-Carlo方法的支持
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
        """根据player_id返回监听器(所有监听器, 并非仅player)
        player_id表明监听器顺序
        """
        if player_id == 1:
            return self.p1.getListeners() + self.p2.getListeners()
        else:
            return self.p2.getListeners() + self.p1.getListeners()
    def getAura(self, player_id)->List[Aura]:
        if player_id == 1:
            return self.p1.getAura()
        else:
            return self.p2.getAura()
    def setAura(self, player_id, new_aura):
        pds = self._getpds(player_id)
        pds.setAura(new_aura)
    def export(self)->GameState:
        #return self.g.clone()
        ##需要将各个监听器的数据统一导出而非clone.
        g = GameState()
        p1 = self.p1.export()
        p2 = self.p2.export()
        g.players.append(p1)
        g.players.append(p2)
        g.history = picklecopy(self.history)
        return g
    def clone(self):
        #g = GameInstance(None)
        #g.p1 = self.p1.clone()
        #g.p2 = self.p2.clone()
        #g.history = picklecopy(self.history)
        return picklecopy(self)
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
    def getOtherChar(self, loc:Location):
        player_id = loc.player_id
        pds = self._getpds(player_id)
        locs = pds.getalives()
        locs = [l for l in locs if l.index != loc.index]
        return locs
    def getstandby(self, player_id)->List[Location]:
        pds = self._getpds(player_id)
        locs = pds.getalives()
        active = pds.history['active']
        locs = [loc for loc in locs if loc.index != active]
        return locs
    def make_damage(self, player_id, target:Union[Location,str], 
                    dvalue, dtype, source = 'active')->List[damage]:
        """
        target,source:定位符. 可以使用active or standby,也可以使用Location.
        (使用active或standby可能不足以定位)
        
        此接口返回一个damage列表. 通常情况下列表长1, 如果使用standby且后台两人存活,那么长2.
        
        此接口永远只返回reason=self的伤害.
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
        return [UseKit(self.nexteid(), -1, ins.player_id, active_loc, ins.kit, t, ins.dice_instance)]
    @translate.register
    def switch(self, ins:Ins.Switch):
        active_loc = self.getactive(ins.player_id)
        return [Switch(self.nexteid(),-1,ins.player_id, active_loc, ins.direction, ins.dice_instance)]
    @translate.register
    def endround(self, ins:Ins.EndRound):
        return [EndRound(self.nexteid(), -1 ,ins.player_id)]
    
    @property
    def mover(self):
        return self.history['mover']
    
    def _execute(self, event:Event):
        if event.eid == -1:
            return []
        else:
            #typename = type(event).__name__.lower()
            #if typename in ('dmg','dealdmg'):
            #    return eval('self.'+typename)(event)
            #print(event)
            #print()
            #else:
            return self.execute(event)
    
    @singledispatchmethod
    def execute(self, event)->Union[List[Event],None]:
        """
        外部不要直接调用execute,而应该调用_execute(完善了各种条件检查)
        """
        
        ##这里使用分派.
        raise TypeError("Unknown type {} for event".format(type(event)))
    
    
    @execute.register
    def dmgtypecheck(self, event:DMGTypeCheck):
        ###可能分裂成DMG或者Reaction.
        ###这里就会直接清理附着, 虽然和正常逻辑不太一样, 不过目前没有任何问题
        player_id = event.player_id
        events = []
        dmg_list = []
        for dmg in event.dmg_list:
            before_aura = self.getAura(player_id)
            after_aura, r = reaction(before_aura, dmg.target, dmg, player_id, event.eid, self)
            if len(r) > 0:
                events += r
            else:
                if dmg.dmgvalue > 0:
                    dmg_list.append(dmg)
            self.setAura(dmg.target.player_id, after_aura)
        if len(dmg_list) > 0:
            events.append(DMG(self.nexteid(),event.eid,event.player_id,dmg_list))
        return events
    
    @execute.register
    def dmg(self, event:DMG):
        ##TODO:转换成DealDMG
        return [DealDMG(self.nexteid(), event.eid, event.player_id, event.dmg_list)]
    
    @execute.register
    def reaction(self, event:Reaction):
        ###TODO: 有副作用的反应先不实现(结晶, 草反应, 超载)
        return [DealDMG(self.nexteid(), event.eid, event.player_id, event.dmg_list)]
    
    
    @execute.register
    def dealdmg(self, event:DealDMG):
        ###调用injure等.
        events = []
        for dmg in event.final_dmg_list:
            if dmg.dmgvalue > 0:
                target = self.get(dmg.target)
                target:Character
                deaths = target.injure(dmg.dmgvalue, event.eid, self)
                events += deaths
                #print("deaths = ", deaths)
        return events
    
    @execute.register
    def usekit(self, event:UseKit):
        active = self.get(event.cur_char)
        active_loc = event.cur_char
        source = event.eid
        if event.kit not in active.no_charge:
            CE = ChargeEnergy(self.nexteid(), source, event.player_id, active_loc, 1)
        SM = SwapMove(self.nexteid(), event.eid, event.player_id, self.mover)
        kit = event.kit
        cast = getattr(active, kit)##释放技能
        active.history[kit+'_use_round'] += 1
        active.history[kit+'_use_total'] += 1
        new_events = cast(self)
        pds = self._getpds(event.player_id)
        pds.dice.consume(event.dice_cost)
        pds.history['plunge'] = False
        return new_events + [CE, SM]
    
    @execute.register
    def charge(self, event:ChargeEnergy):
        char = self.get(event.loc)
        char:Character
        char.charge(event.energy_slots, event.eid, self)
        return []
    
    @execute.register
    def swapmove(self, event:SwapMove):
        oppo = self._getpds(event.player_id)
        if not oppo.history['endround']:
            if event.ifswap:
                self.history['mover'] = 3 - self.history['mover']
        return []
    @execute.register
    def death(self, event:Death):
        death_player = event.player_id
        pds = self._getpds(death_player)
        if len(pds.getalives()) == 0:
            self.history['winner'] = 3 - death_player
            return []
        else:
            active_loc = self.getactive(death_player)
            if active_loc.index == event.char_loc.index:
                self.last_phase = self.history['phase']
                self.history['phase'] = 'deathswitch'
            return []
    
    @execute.register
    def switch(self, event:Switch):
        ##注意如果是deathswitch要转换至last_phase
        ##注意只剩一个人时将是无效切人.
        pds = self._getpds(event.player_id)
        alives = pds.getalives()
        if len(alives) <= 1:
            return []
        active = self.getactive()
        chars = pds.charView(active.index)
        increment = event.direct
        i = increment
        while chars[i].died():
            i += increment
        char = chars[i]
        pds.history['active'] = char.loc.index
        pds.history['plunge'] = True
        pds.dice.consume(event.dice_cost)
        event.succeed = True
        if self.history['phase'] == 'deathswitch':
            self.history['phase'] = self.last_phase
        return []
    
    def _search_listener(self, listener_type, summon_list):
        index = -1
        for i, s in enumerate(summon_list):
            if isinstance(s, listener_type):
                index = i
                break
        return index
    
    @execute.register
    def summon(self, event:Summon):
        pds = self._getpds(event.player_id)
        index = self._search_listener(event.summoned, pds.summon)
        if index == -1:
            if len(pds.summon) >= 4:
                ##召唤区已满
                return []
            s = event.summoned()
            #s:Summon
            loc = Location(event.player_id,'Summon',len(pds.summon))
            s.place(loc)
            pds.summon.append(s)
        else:
            pds.summon[index].update(event.summoned.init_usage)
            
        

    @execute.register
    def over(self, event:Over):
        """
        基本上成了状态机核心
        """
        if type(event.overed) == EndRound:
            oppo_id = get_oppoid(event.player_id)
            oppo = self._getpds(oppo_id)
            if not oppo.history['endround']:
                return [SwapMove(self.nexteid(), event.eid, event.player_id, event.player_id)]
            else:
                self.history['phase'] = 'end'
                return [SwapMove(self.nexteid(), event.eid, event.player_id, event.player_id)] + \
                    [EndPhase(self.nexteid(), event.eid, event.player_id)]
        elif type(event.overed) == EndPhase:
            self.history['phase'] = 'roll'
            first = self.mover
            ###TODO: V1全万能
            return [GenerateDice(self.nexteid(), event.eid, first, DicePattern(omni = 8)),
                GenerateDice(self.nexteid(), event.eid, 3 - first, DicePattern(omni = 8)), RollPhase(self.nexteid(), event.eid,event.player_id)]
        elif type(event.overed) == RollPhase:
            self.history['phase'] = 'start'
            return [StartPhase(self.nexteid(), event.eid, event.player_id)]
        return []
    
    
    @execute.register
    def endround(self, event:EndRound):
        pds = self._getpds(event.player_id)
        pds.history['endround'] = True
        return []
    @execute.register
    def endphase(self, event:EndPhase):
        ###最重要的维护history的部分.
        ###几乎所有history变量在这里都需要重置, 除了total_use.
        ##特别乐的是startphase要在endphase维护.
        first = self.mover
        pfirst = self._getpds(first)
        psecond = self._getpds(3 - first)
        pfirst.startphase_reset()
        psecond.startphase_reset()
        
        return [DrawCard(self.nexteid(),event.eid, event.player_id, 2)]
    
    @execute.register
    def rollphase(self, event:RollPhase):
        ###TODO: V1跳过重骰阶段. 
        ## 注意rollphase需要两个人重骰.
        return []
    @execute.register
    def startphase(self, event:StartPhase):
        self.history['phase'] = 'combat'
        return []
    @execute.register
    def generatedice(self, event:GenerateDice):
        pds = self._getpds(event.player_id)
        if self.estimator is not None:##V1全万能也不上
            di = self.estimator(event, self)
            pds.dice.addDiceInstance(di)
        else:
            pds.dice.addDice(event.dice_pattern)
        return []
    
def swap_ele(e1,e2):
    if e1 > e2:
        return e2,e1
    else:
        return e1,e2
    
def apply_react(aura, application, loc:Location, dmg:damage, 
                player_id, source_id, g:GameInstance)->Tuple[Aura,List[Reaction]]:
    """火冰雷水的反应
    
    aura:附着元素(包括empty等)
    application:施加元素(后手元素)
    
    返回新的aura和反应列表. 注意loc和Player_id往往不是同一方. loc是反应发生的精确位点
    """
    if aura == Aura.died:
        return aura,[]
    if aura == Aura.empty:
        return application, []
    t, a = swap_ele(aura, application)
    ###按序排列好后, 之后的分支无需判断前面的元素.
    ###也不需要判断geo和anemo(前面已处理过)
    #print("t,a =", t, ', ', a)
    re = 'NoReaction'
    new_aura = aura
    if t == Aura.pyro:
        table = {
            Aura.cryo:'melt',
            Aura.electro:'overloaded',
            Aura.hydro:'vaporize',
            Aura.dendro:'burning',
            Aura.crydendro:'melt',
            #Aura.anemo:'swirl',
            #Aura.geo:'crystallize'
        }
        re = table.get(a, 'NoReaction')
        pass
    elif t == Aura.cryo:
        table = {
            Aura.electro:'superconduct',
            Aura.hydro:'frozen',
            Aura.dendro:'NoReaction',
            Aura.crydendro:'NoReaction',
            #Aura.anemo:'swirl',
            #Aura.geo:'crystallize'
        }
        re = table.get(a, 'NoReaction')
        pass
    elif t == Aura.electro:
        table = {
            Aura.hydro:'electrocharge',
            Aura.dendro:'quicken',
            Aura.crydendro:'superconduct',
            #Aura.anemo:'swirl',
            #Aura.geo:'crystallize'
        }
        re = table.get(a, 'NoReaction')
        pass
    elif t == Aura.hydro:
        table = {
            Aura.dendro:'bloom',
            Aura.crydendro:'frozen',
            #Aura.anemo:'swirl',
            #Aura.geo:'crystallize'
        }
        re = table.get(a, 'NoReaction')
        pass
    elif t == Aura.dendro:
        ###草不会与crydendro反应, 也不会与geo,anemo反应
        return aura, []
    elif t == Aura.crydendro:
        return aura, []
    else:
        raise Exception("Unexpected Elemental Reaction with {} and {}".format(t,a))

    ###这里需要处理好dmg.
    plus_two = ['melt','overloaded','vaporize']
    pierce = ['electrocharge','superconduct']
    plus_one = ['burning','bloom','frozen','quicken']
    
    dmg_list = []
    if dmg.dmgvalue > 0:##非伤害效应无视加伤效果
        if re in plus_two:
            dmg.dmgvalue += 2
        elif re in plus_one:
            dmg.dmgvalue += 1
        elif re in pierce:
            dmg.dmgvalue += 1
            standbys = g.getOtherChar(loc)
            for standby in standbys:
                dmg_list.append(damage(dmg.attacker,standby, DMGType.pierce, 1))
        elif re == 'NoReaction':
            pass
        else:
            raise Exception('Unknown Reaction {}!'.format(re))
    dmg_list = [dmg] + dmg_list
    
    if re != 'NoReaction':
        r_event = Reaction(g.nexteid(),source_id, player_id, loc, re, 
                           getattr(DMGType,aura.name), getattr(DMGType, application.name),dmg_list)
        if new_aura == Aura.crydendro:
            new_aura = Aura.dendro##一定与冰先反应
        else:
            new_aura = Aura.empty
        return new_aura, [r_event]
    else:
        return new_aura, []

def reaction(target_aura:List[Aura],  target_loc:Location,
             dmg:damage,player_id, source_id, g:GameInstance)->Tuple[List[Aura], List[Union[Reaction,DMG]]]:
    """
    返回反应后的aura和反应事件或者伤害事件(反应事件可能有多个)
    
    注意, target_aura是一个aura列表, 装载了对方所有的角色的aura情况.
    Reaction事件中已经完成基础的加伤事件. 
    """
    if dmg.dmgtype == DMGType.physical or dmg.dmgtype == DMGType.pierce:
        return target_aura, []
    application = Aura.__dict__[dmg.dmgtype.name]
    application:Aura
    dmg_list = [dmg]
    target = target_loc.index
    t_aura = target_aura[target]
    if t_aura == Aura.empty:
        if application in [Aura.anemo, Aura.geo]:
            return target_aura, []
        else:
            target_aura[target] = application
            return target_aura, []
    elif t_aura == application:
        return target_aura, []
    elif t_aura == Aura.dendro and application == Aura.cryo or application == Aura.dendro and t_aura == Aura.cryo:
        target_aura[target] = Aura.crydendro
        return target_aura, []
    elif t_aura == Aura.dendro and (application == Aura.anemo or application == Aura.geo):
        return target_aura, []
    elif application == Aura.geo:
        if t_aura in (Aura.pyro, Aura.cryo, Aura.crydendro, Aura.hydro, Aura.electro):
            if t_aura != Aura.crydendro:
                target_aura[target] = Aura.empty
            else:
                target_aura[target] = Aura.dendro
            auraName = t_aura.name
            dmg_list[0].dmgvalue += 1##结晶增伤1
            return target_aura, [Reaction(g.nexteid(),source_id,
                                          player_id, target_loc,'crystallize', getattr(DMGType, auraName), DMGType.geo, dmg_list)]
        pass
    elif application == Aura.anemo:
        if t_aura in (Aura.pyro, Aura.cryo, Aura.crydendro, Aura.hydro, Aura.electro):
            if t_aura != Aura.crydendro:
                target_aura[target] = Aura.empty
            else:
                target_aura[target] = Aura.dendro
            r = [Reaction(g.nexteid(),source_id,
                                        player_id, target_loc,'swirl', getattr(DMGType, t_aura.name), DMGType.anemo, dmg_list)]
            ###然后计算后台反应. 如果有反应, 产生Reaction事件, 否则产生DMG事件.
            ###小心深拷贝问题
            others = g.getOtherChar(target_loc)
            for other in others:
                other_aura = target_aura[other.index]
                swirl_damage = damage(dmg.attacker,other,getattr(DMGType, t_aura.name),1,'swirl')
                after_aura, events = apply_react(other_aura, t_aura, other, swirl_damage, player_id, r[0].eid, g)
                target_aura[other.index] = after_aura
                if len(events) > 1:
                    raise RuntimeError("Multiple Reactions while dealing with swirl!")
                elif len(events) == 0:
                    r.append(DMG(g.nexteid(), r[0].eid,player_id, [swirl_damage]))
                else:
                    r += events
            return target_aura, r
        pass
    else:
        t, r = apply_react(t_aura, application,target_loc,dmg,player_id, source_id, g)
        target_aura[target] = t
        return target_aura, r
    return target_aura, []