import sys
sys.path.append('..')
from src.core.GameState import GameState,Box
import numpy as np

from src.core.base import DiceInstance,DicePattern, Location
from src.core.GameInstance import GameInstance
from src.character.utils import name2char
from src.core.Instruction import Instruction
import src.core.Instruction as Ins
import src.core.Event as Event
###Instruction和Event有一点重名.
from typing import Union, List, Tuple, Any,Dict


def activate(gs:GameState)->GameState:
    """gamestate冷启动.
    
    即第一次生成GameState时,由于数据存在character中, 需要去取出参数.
    
    name2char -> export
    """
    for i in [0,1]:
        gs.players[i].history['player_id'] = i + 1
        chars = gs.players[i].char
        new_chars = []
        for char in chars:
            Char = name2char(char)
            new_chars.append(Char.export())
        gs.players[i].char = new_chars
    return gs

from typing import TypedDict

def fake_callback(*args):
    return Event.Event(-1,-1,-1)

class Game:
    def __init__(self, gs = None):
        """
        注意gs暂时不支持中途加载
        """
        if gs == None:
            self.g = None
        else:
            self.g = GameInstance(activate(gs.clone()))
    def clone(self)->"Game":
        newgame = Game()
        newgame.load(self.g.clone())
        return newgame
    def firstfive(self,callback1, callback2):
        ####双方抽5
        ###player选择换牌(自己去hand看去)
        ###player同时选择出战角色
        ###开始(设置mover,发送一条Over(EndPhase), 进入proceed流程).
        pass
    def swaphand(self, player_id, indices:List[int]):
        pass
    def choose_active(self,player_id, active):
        self.g.choose_active(player_id, active)
    def initiate(self, p1_active, p2_active, callback):
        self.g.choose_active(1, p1_active)
        self.g.choose_active(2, p2_active)
       # start = Event.EndPhase(0,-1,1)
       # self.g.history['mover'] = 1
       # self.g._issue(Event.Over(0,-1, 1, start), callback)
        self.g._issue(Event.GameStart(0,-1,1), callback)
        assert self.g.history['mover'] == 1
    def load(self, g:GameInstance):
        self.g = g
    def proceed(self, ins:Instruction, new_game, callback):
        if ins.player_id != self.mover:
            raise ValueError("Now it's not your turn!")
        if new_game:
            g = self.clone()
            g.g.proceed(ins, callback = callback)
            return g
        else:
            self.g.proceed(ins, callback = callback)
    def terminated(self):
        if self.g.history['rounds'] > 8 or self.g.history['winner'] > 0:
            return True
        return False
    @property
    def winner(self):
        return self.g.history['winner']
    
    @property
    def mover(self):
        return self.g.history['mover']
    
    @property
    def phase(self):
        return self.g.history['phase']
    
    def state(self,player_id)->np.ndarray:
        pass
    
    def valids(self,player_id)->np.ndarray:
        pass
    
    def getIns(self, player_id, action:str)->Union[Instruction,None]:
        """使用该方法获得一个指令原型,或者None(如果这非法)
        
        指令原型中包含了该行动所需要支付的真实费用DicePattern.
        你仍需要检查骰池以确定实际支付的骰子. 
        
        一个标准的流程是:
        ins = getIns(name)
        ins.dice_instance = choose_dice(ins.dice_pattern, dicepool)
        g = game.proceed(ins)
        
        action列表:
        na, skill, burst, sp1, sp2
        switch next, switch previous
        end round,
        play card X(X=1--10)
        tune card X(X=1--10)
        
        前五个行动和最后两个行动需要自行确定内部参数(目标列表/费用)
        
        随后传入proceed.
        
        valids返回的掩码对应上面的action列表. 需要提醒的是,最后两个行动每个都包含10个具体行动, 因此掩码会更长一些.
        """
        def count(dp:DicePattern):
            n = 0
            for k,v in dp.to_dict().items():
                n += v
            return n
        keys = action.split(' ')
        ###V1全部使用万能骰
        g = self.g
        dice = g._getpds(player_id).dice
        if keys[0] in ('na','skill','burst','sp1','sp2'):
            active = g.getactive(player_id)
            c = g.get(active)
            costP = c.dice_cost[keys[0]]
            dicen = count(costP)
            cost = DiceInstance(omni = dicen)
            if dice.num() < dicen:
                return None
            if keys[0] == 'burst' and c.energy < c.maxenergy:
                return None
            return Ins.UseKit(player_id,costP,costP,cost,keys[0])
        elif keys[0] == 'switch':
            if dice.num() < 1:
                return None
            pds = g._getpds(player_id)
            others = pds.getalives()
            if len(others) <= 1:
                return None
            proto = Ins.Switch(player_id, DicePattern(omni=1),DicePattern(omni=1), DiceInstance(omni=1), 1)
            if keys[1] == 'next':
                proto.direction = 1
            else:
                if len(others) == 2:
                    return None
                proto.direction = -1
            return proto
        elif keys[0] == 'end':
            return Ins.EndRound(player_id, None,None,None)
        else:
            raise NotImplementedError
        return None
        
if __name__ == "__main__":
    b1 = Box(['Diluc','Kaeya'],[])
    b2 = Box(['Sucrose','Diluc'],[])
    g = GameState(b1,b2)
    g = activate(g)
    print(g.players[0].char)