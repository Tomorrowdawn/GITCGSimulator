import sys
sys.path.append('..')
from src.core.GameState import GameState,Box
import numpy as np

from src.core.GameInstance import GameInstance
from src.character.utils import name2char
from src.core.Instruction import Instruction
import src.core.Instruction as Ins
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
class Game:
    def __init__(self):
        self.gs = None
        pass
    def clone(self)->"Game":
        newgame = Game()
        newgame.load(self.gs.clone())
        return newgame
    def firstfive(self):
        ####双方抽5
        ###player选择换牌(自己去hand看去)
        ###player同时选择出战角色
        ###开始(设置mover,发送掷骰Event, 进入proceed流程).
        pass
    def swaphand(self, player_id, indices:List[int]):
        pass
    def choose_active(self,player_id, active):
        pass
    def initiate(self,gs:GameState):
        self.gs = activate(gs.clone())
    def load(self, gs:GameState):
        self.gs = gs.clone()
    def proceed(self, ins:Instruction)->"Game":
        NewGame = Game()
        GI = GameInstance(self.gs)
        GI.proceed(ins)
        gs = GI.export()
        NewGame.load(gs)
        return NewGame
    @property
    def mover(self):
        return self.gs.history['mover']
        pass
    
    @property
    def phase(self):
        return self.gs.history['phase']
        pass
    
    def state(self,player_id)->np.ndarray:
        pass
    
    def gamestate(self)->GameState:
        return self.gs
    
    def valids(self,player_id)->np.ndarray:
        pass
    
    def getIns(self, action:str)->Union[Instruction,None]:
        """使用该方法获得一个指令原型,或者None(如果这非法)
        
        指令原型中包含了该行动所需要支付的真实费用DicePattern.
        你仍需要检查骰池以确定实际支付的骰子.
        
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
        keys = action.split(' ')
        if keys[0] == 'na':
            pass
        
        pass
if __name__ == "__main__":
    b1 = Box(['Diluc','Kaeya'],[])
    b2 = Box(['Sucrose','Diluc'],[])
    g = GameState(b1,b2)
    g = activate(g)
    print(g.players[0].char)