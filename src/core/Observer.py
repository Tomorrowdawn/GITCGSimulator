import sys

sys.path.append("..")
sys.path.append("../..")

from src.core.GameInstance import GameInstance,PlayerInstance,Listener,Character
import torch


class Observer:
    def observe(self, gi:GameInstance,player_id):
        """
        返回player_id视角下的特定的数据格式.
        """
        pass
    def winner(self, gi:GameInstance):
        """
        1 or 2 or None if not terminated.
        """
        if gi.history['winner'] <= 0:
            return None
        return gi.history['winner']


class TensorObserver(Observer):
    
    listener_length = 3###name占一个, usage占一个, 其他占一个.
    teambuff_num = 5
    charbuff_num = 4
    char_length = 4 + charbuff_num * listener_length + 3
    total_length = 190
    def __init__(self, name2id:dict) -> None:
        """
        name2id:将字符串转换成id的字典. 注意, 字符串与类名对应.
        name可能有角色也可能有牌等等, 因此id不一定是唯一的(仅在某个确定域中唯一也可以).
        """
        super().__init__()
        self.lookup = name2id
        
    def listener_observe(self, listener:Listener)->torch.TensorType:
        lid = self.lookup[type(listener).__name__]
        embed = torch.zeros(self.listener_length)
        embed[0] = lid
        i = 1
        for var in listener._vars:
            embed[i] = int(getattr(listener, var))
            i += 1
        return embed
    def char_observe(self, c:Character):
        #c.aura, c.hp, c.energy, c.weapon, c.artifact, c.talent, c.buff, c.history
        cid = self.lookup[type(c).__name__]
        if c.hp <= 0:
            embed = torch.zeros(self.char_length)
            embed[0] = cid
            return embed
        base = torch.tensor([cid, int(c.aura), c.hp, c.energy])
        buffs = []
        for b in c.buff[:self.charbuff_num]:
            buffs.append(self.listener_observe(b))
        for _ in range(self.charbuff_num - len(buffs)):
            buffs.append(torch.zeros(self.listener_length))
        history_order = ['frozen','petrified','saturated']
        ###只管这几个算了
        history = torch.zeros(len(history_order))
        for i, h in enumerate(history_order):
            history[i] = int(c.history[h])
        return torch.cat([base, *buffs, history])
        
    def player_observe(self, p:PlayerInstance)->torch.TensorType:
        #p.deck, p.hand, p.support, p.char,p.buff,p.summon, p.dice,p.history
        ####TODO: 暂时忽略deck, hand, support
        embed = []
        for c in p.char:
            embed.append(self.char_observe(c))
        k = 0
        while k < len(p.buff):
            embed.append(self.listener_observe(p.buff[k]))
            k += 1
        while k < self.teambuff_num:
            embed.append(torch.zeros(self.listener_length))
            k += 1
        summon = [torch.zeros(self.listener_length) for i in range(4)]
        for i, s in enumerate(p.summon):
            summon[i] = self.listener_observe(s)
        embed.extend(summon)
        
        dice_types =  ['omni', 'pyro','electro','geo','anemo','dendro','hydro','cryo']
        dices = torch.zeros(8)
        dice = p.dice.dice.to_dict()
        for i, d in enumerate(dice_types):
            dices[i] = dice[d]
        history_list = ['active','dieThisRound','plunge','endround']
        history = torch.zeros(4)
        for i, h in enumerate(history_list):
            history[i] =  int(p.history[h])
        embed.append(torch.tensor([p.dice.num()]))
        embed.append(history)
        public = embed
        private = [dices]
        return torch.cat(public), torch.cat(private)
    def observe(self, gi: GameInstance, player_id):
        #gi.p1, gi.p2, gi.history
        #if player_id == 1:
        pub1, pvt1 = self.player_observe(gi.p1)
        pub2, pvt2 = self.player_observe(gi.p2)
        if player_id == 1:
            embed = [pub1,pvt1, pub2]
        else:
            embed = [pub2,pvt2, pub1]
        #embed = [self.player_observe(gi.p1), self.player_observe(gi.p2)]
        history_list = ['mover','phase','rounds','winner']
        phases = ['firstfive', 'roll', 'start', 'combat', 'end', 'deathswitch']
        phases = {k:i for i, k in enumerate(phases)}
        history = torch.zeros(4)
        history[0] = gi.history['mover']
        history[1] = phases[gi.history['phase']]
        history[2] = gi.history['rounds']
        history[3] = gi.history['winner']
        embed.append(history)
        return torch.cat(embed)