import sys
from src.core.Event import Any
sys.path.append('..')
from src.game import Game
from src.core.GameInstance import GameInstance,PlayerInstance,Aura
from src.core.Event import *
import time
from src.core.EventManage import EventHub
from src.core.Observer import TensorObserver
import torch
import json

from src.core.GameInstance import apply_react, reaction, GameInstance
from src.core.GameState import Location, Aura, GameState, Box
from src.game import activate, Game, fake_callback
from tqdm import tqdm
from src.agent.alphabeta import Searcher

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

POSSIBLE_MOVES = ['burst', 'skill','na', 'switch next','switch previous','end round']
MOVE2INT = {k:i for i, k in enumerate(POSSIBLE_MOVES)}
MOVE_CHOICES = len(POSSIBLE_MOVES)
import random

class RandomPlayer:
    def callback(self, g:GameInstance,event, event_set, event_queue):
        if isinstance(event, Death) and g.history['phase'] == 'deathswitch':
            active = g.getactive(event.player_id)
            direct = random.choice([1,-1])
            s = Switch(g.nexteid(), event.eid, event.player_id, active, direct)
            return s
        else:
            return Event(-1,-1,-1)
    def search(self, g, *args, **kwargs):
        def moves():
            ms = []
            for m in POSSIBLE_MOVES:
                move = g.getIns(g.mover, m)
                if move is not None:
                    ms.append(move)
            return ms
        return random.choice(moves())

class MCTS:
    class Node:
        def __init__(self, parent, g:Game, policy, valids, obs:TensorObserver) -> None:
            self.p = parent
            self.g = g
            if g.terminated():
                self.expanded = True
            else:
                self.expanded = False
            self.offsprings = {}
            self.valids = valids
            self.policy = policy.flatten()
            self.obs = obs
            self.action_values = torch.zeros(MOVE_CHOICES)
            self.action_visits = torch.zeros(MOVE_CHOICES)
            #self.rng = nodes
        def expand(self, move, callback, net):
            """
            返回该move相对于node的价值(外围无需取反)
            """
            if self.expanded:
                raise ValueError("Unexcepted expand")
            g = self.g
            # = len(self.valid_moves)
            #for move in self.moves:
            ins = g.getIns(g.mover, move)
            
            child = g.proceed(ins, new_game= True, callback = callback)
                #q,_ = net(g)
            valids = torch.zeros(MOVE_CHOICES)
            for i, a in enumerate(POSSIBLE_MOVES):
                ins = child.getIns(child.mover, a)
                if ins is not None:
                    valids[i] = 1
            with torch.no_grad():
                state = self.obs.observe(child.g, child.mover)
                state = torch.unsqueeze(state.to(DEVICE), 0)
                policy, value = net(state)
            policy = policy.cpu() * valids
            policy = policy / torch.sum(policy)
            v = value.cpu().item()
            if child.mover != g.mover:
                v = -v###FIXME: 有问题. 修改此处后训练胜率一直为0.00
            self.action_values[MOVE2INT[move]] = v
            child = MCTS.Node(self, child, policy, valids, self.obs)
            self.offsprings[move] = child
            return v
    def __init__(self, net, id_path) -> None:
        self.net = net
        with open(id_path) as p:
            ids = json.load(p)
        self.obs = TensorObserver(ids)
        
    def callback(self, g:GameInstance,event, event_set, event_queue):
        if isinstance(event, Death) and g.history['phase'] == 'deathswitch':
            active = g.getactive(event.player_id)
            #temp = g.clone()
            best_u = -float('inf')
            best_s = None
            for direct in (1,-1):
                s = Switch(g.nexteid(), event.eid, event.player_id, active, direct)
                game = Game()
                game.g = g.clone()
                u = 0
                eh = EventHub(event_set + [s] + event_queue)
                eh.checkout(game.g, self.callback)
                #if self.searching:
                node = self._game2node(game)
                if self.searching:
                    sims = 5
                else:
                    sims = 25
                for sim in range(sims):
                    v = self._search(node)
                    u += v
                u /= sims
                if event.player_id != game.mover:
                    u = -u
                if u > best_u:
                    best_u = u
                    best_s = s
            return best_s
        else:
            return Event(-1,-1,-1)
    def _eval(self, node):
        if node.g.winner < 0:
            return -1
        if node.g.winner == node.g.mover:
            return 1
        else:
            return -1
    def _search(self, node:"MCTS.Node"):
        self.nodes += 1
        
        if node.g.terminated():
            return self._eval(node)
        
        #node = root
        #while node.expanded or not node.g.terminated():
            #max_u ,best_a = -float("inf"), None
        valids = node.valids
        #print("valids = ", valids)
        u = node.action_values + self.c_puct * node.policy * torch.sqrt(torch.sum(node.action_visits)) / (1 + node.action_visits)
        u[valids==0] = -float('inf')
        best_a = torch.argmax(u)
        net = self.net
        
        a = POSSIBLE_MOVES[best_a.item()]
       # print("action = {}".format(a))
        child = node.offsprings.get(a, None)
        if child == None:
            v = node.expand(a,self.callback, net)
            child = node.offsprings[a]
            if child == None:
                raise ValueError("Fake Expand for move {}".format(a))
            return v
        v = self._search(child)
        if child.g.mover != node.g.mover:
            v = -v
        a = best_a.item()
        N, Q = node.action_visits[a], node.action_values[a]
        node.action_values[a] = (N*Q + v)/(1+N)
        node.action_visits[a] += 1
        return v
    def _game2node(self, g:Game, parent = None):
        state = self.obs.observe(g.g, g.mover)
        state = torch.unsqueeze(state.to(DEVICE),0)
        self.net.eval()
        with torch.no_grad():
            policy, _ = self.net(state)
        valids = torch.zeros(MOVE_CHOICES)
        for i, a in enumerate(POSSIBLE_MOVES):
            ins = g.getIns(g.mover, a)
            if ins is not None:
                valids[i] = 1
        policy = policy.cpu() * valids
        policy = policy / torch.sum(policy)
        root = MCTS.Node(parent, g, policy, valids, self.obs)
        return root
    def search(self, g:Game, time_limit, noised = False, sims = 25)->str:
        """
        self.pi可以获取策略概率分布.
        """
        self.c_puct = 1/1.44
        self.nodes = 0
        self.pi = torch.ones(MOVE_CHOICES)/MOVE_CHOICES
        self.time_limit = time_limit
        state = self.obs.observe(g.g, g.mover)
        state = torch.unsqueeze(state.to(DEVICE),0)
        self.searching = True
        self.net.eval()
        with torch.no_grad():
            policy, _ = self.net(state)
        valids = torch.zeros(MOVE_CHOICES)
        for i, a in enumerate(POSSIBLE_MOVES):
            ins = g.getIns(g.mover, a)
            if ins is not None:
                valids[i] = 1
        policy = policy.cpu()
        if noised:
            policy = 0.75 * policy + 0.25 * np.random.dirichlet([1.0 for _ in policy])
        policy = policy * valids
        policy = policy / torch.sum(policy)
        root = MCTS.Node(None, g, policy, valids, self.obs)
        self.start_time = time.time()
        for _ in range(sims):
            self._search(root)
            #print("searched node : %d" % self.nodes)
            #if time.time() - self.start_time > time_limit:
            #    break
       # sims_time = time.time() - self.start_time
       # print("average sim time = {:.3f}s".format(sims_time/sims))

        self.pi = root.action_visits / torch.sum(root.action_visits)
        #print("action visits = ", root.action_visits)
        best = torch.argmax(root.action_visits)
        move = POSSIBLE_MOVES[best.item()]
        return g.getIns(g.mover, move)
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn


class CatNet(nn.Module):
    def __init__(self, indim = 190, action_dim = MOVE_CHOICES) -> None:
        super().__init__()
        #self.encoder = nn.Linear(indim, indim * 2)
        topology = [indim, indim * 2, indim, 50]
        topo = []
        for i, j in zip(topology[:-1], topology[1:]):
            topo.extend([
                nn.Linear(i,j),
                nn.ReLU(),
                nn.BatchNorm1d(j)##FIXME: 先BN后RELU. 但是已经训练很久了,不要动网络结构了.
            ])
        self.hid = nn.Sequential(*topo)
        self.policy_head = nn.Sequential(
            nn.Linear(50, action_dim),
            nn.LogSoftmax(-1)
        )
        self.value_head = nn.Sequential(
            nn.Linear(50, 1),
            nn.Tanh()
        )
    def forward(self, x):
        x = self.hid(x)
        pi = self.policy_head(x)
        v = self.value_head(x)
        return torch.exp(pi), v
    def predict(self, x):
        """
        返回LogSoftmax
        """
        x = self.hid(x)
        pi = self.policy_head(x)
        v = self.value_head(x)
        return pi, v
    

import random
import numpy as np
class GIDataset(Dataset):
    def __init__(self, dataset) -> None:
        super().__init__()
        self.d = dataset
    def __len__(self):
        return len(self.d)
    def __getitem__(self, index) -> Any:
        state, (pi, v) = self.d[index]
        return state, {'pi':pi, 'v':v}
import math

from datetime import datetime

class Trainer:
    """
    通常, 你需要修改episode方法(来生成特定于你的数据集)
    和learn方法(学习你的特定数据集)
    
    如果你的数据集继承自GIDateset并且仅修改__getitem__方法, 你不需要修改train. 
    但你需要在__init__方法中修改self.dataset
    
    否则你需要修改train来完成自己的训练.
    """
    def __init__(self, mcts:MCTS, checkpoint_root) -> None:
        self.algo = mcts
        self.checkpoint_root = checkpoint_root
        self.loss = []
        self.epoch_count = 0
        self.init_lr = 0.01
        self.dataset = GIDataset([])
    def lr(self):
        if self.init_lr < 1e-5:
            return 1e-5
        self.init_lr *= 0.9
        return self.init_lr
    def set_initgame_param(self):
        pass
    
    def initgame(self):
        b1 = Box(['Fischl','Ayaka','Sucrose'],[])
        b2 = Box(['Diluc','Kaeya','Sucrose'],[])
        state = GameState(b1,b2)
        g = Game(state)
        g.initiate(0, 0, fake_callback)
        return g
    def episode(self, g:Game, sims):
        g = g.clone()
        examples = []
        obser = self.algo.obs
        while not g.terminated():
            with torch.no_grad():
                m = self.algo.search(g, 1, sims, noised = True)
            state = obser.observe(g.g, g.mover)
            example = [g.mover, state , self.algo.pi]
            examples.append(example)
            pi = self.algo.pi
            pi = np.array(pi)
            if np.sum(pi) > 1:
                pi = pi / np.sum(pi)###缩小浮点误差
            
            if math.isnan(pi[0]):
                print("g history = ", g.g.history)
                print("g dice num = ", g.g.p1.dice.num(), ', ', g.g.p2.dice.num())
                raise Exception("Nan")
            move = np.random.choice(len(pi), p = pi)
            move = POSSIBLE_MOVES[move]
            ins = g.getIns(g.mover, move)
            g.proceed(ins, False, self.algo.callback)
        dataset = []
        winner = g.winner
        if winner < 0:
            hp1 = 0
            for c in g.g.p1.char:
                hp1 += c.hp
            hp2 = 0
            for c in g.g.p2.char:
                hp2 += c.hp
            if hp1 > hp2:
                winner = 1
            else:
                winner = 2
        for mover, state, pi in examples:
            #if winner < 0:
            #    dataset.append( (state,[pi,-1]) )
            if mover == winner:
                dataset.append( (state, [pi,1]) )
            else:
                dataset.append( (state,[pi,-1]) )
        return dataset
    def train(self, iters, games_per_iters, name = 'catnet' ,sims = 25, lr = 0.01):
        dataset = self.dataset
        self.epoch_count = 0
        self.init_lr = lr
        g = self.initgame()
        for iter in range(iters):
            if len(dataset) > 50000:
                dataset.d = dataset.d[-50000:]
            print("iter = %d" % iter)
            for game in tqdm(range(games_per_iters)):
                dataset.d += self.episode(g, sims)
            self.learn(dataset)
            self.save_checkpoint(dataset, name = name + '.pt')
            wr = self.test(Searcher(), 10, 1)
            if wr >= 0.7:
                self.save_checkpoint(dataset, name = name + '{:02d}.pt'.format(int(wr * 100)))
        pass
    def save_checkpoint(self, dataset, name = 'catnet.pt'):
        path = self.checkpoint_root + '/' + name
        state_dict = {
            'model':self.algo.net.state_dict(),
            'dataset':dataset
        }
        torch.save(state_dict,path)
    def learn(self, trainset:GIDataset):
        self.algo.net.train()
        lr = self.lr()
        net = self.algo.net
        net:CatNet
        loader = DataLoader(trainset, 128, shuffle = True)
        vloss = nn.MSELoss()
        optimizer = torch.optim.Adam(net.parameters(),lr = lr)
        for epoch in range(10):
            for i, (inputs, labels) in enumerate(loader):
                if inputs.size()[0] <= 1:
                    continue
                pis, vs = labels['pi'], labels['v']
                inputs = inputs.to(DEVICE)
                pis = pis.float().to(DEVICE)
                vs = vs.float().to(DEVICE)
                o_pis, o_vs = net.predict(inputs)
                
                optimizer.zero_grad()
                loss = vloss(o_vs.flatten(), vs) + self.piloss(o_pis, pis)
                loss.backward()
                optimizer.step()
                self.loss.append(loss.detach().cpu().item())
        pass
    def piloss(self, predict, target):
        """
        注意net的输出要是logsoftmax
        """
        return -torch.sum(predict * target) / target.size()[0]
    def test(self, opponent, game_num, time_per_step = 1, verbose = False):
        wins = 0
        origin_g = self.initgame()
        for _ in range(game_num):
            g = origin_g.clone()
            player_id = random.randint(1,2)
            if verbose:
                print("player id = %d" % player_id)
            while not g.terminated():
                if g.mover == player_id:
                    m = self.algo.search(g, time_per_step, 30)
                    g.proceed(m, False, self.algo.callback)
                else:
                    m = opponent.search(g, time_per_step, verbose = False)
                    g.proceed(m, False, opponent.callback)
            if g.winner == player_id:
                if verbose:
                    print("win")
                wins += 1
            else:
                if verbose:
                    print("lose")
        print("test win rate = {}".format(wins/game_num))
        return wins/game_num
    
class PrinceDataset(GIDataset):
    def __getitem__(self, index) -> Any:
        state, (pi, v, importancy, rounds, hp_diff) = self.d[index]
        return state, {'pi':pi,
                       'v':v,
                       'importancy':importancy,
                       'rounds':rounds,
                       'hp_diff':hp_diff
                    }
class PrinceNet(nn.Module):
    def __init__(self, indim = 190, action_dim = MOVE_CHOICES) -> None:
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(indim, indim),
            nn.ReLU()
        )
        embed_size = 50
        topology = [indim, embed_size]
        topo = []
        for i, j in zip(topology[:-1], topology[1:]):
            topo.extend([
                nn.Linear(i,j),
                nn.BatchNorm1d(j),
                nn.ReLU()
            ])
        self.hid = nn.Sequential(*topo)
        self.policy_head = nn.Sequential(
            nn.Linear(embed_size, action_dim),
            nn.LogSoftmax(-1)
        )
        pool_window = 10
        self.avgpool = nn.AvgPool1d(pool_window)
        self.maxpool = nn.MaxPool1d(pool_window)
        def pooling(x):
            ##X shape = (N, L)
            ##需要插入一个通道,即(N,1,L)
            x = torch.unsqueeze(x, dim = 1)
            y1 = self.avgpool(x)
            y2 = self.maxpool(x)
            ###y1,y2:(N,1,L_out). 再挤压掉通道
            y1 = torch.squeeze(y1)
            y2 = torch.squeeze(y2)
            ##注意连接最后一个
            return torch.cat([y1,y2],dim = -1)
        self.pool = pooling
        pool_size = embed_size // pool_window
        self.value_head = nn.Sequential(
            #nn.AvgPool1d(10),
            nn.Linear(pool_size * 2, 1),
            nn.Tanh()
        )
        self.imp_head = nn.Sequential(
            nn.Linear(pool_size * 2, 3),
            nn.Sigmoid()
        )
        self.round_head = nn.Sequential(
            nn.Linear(pool_size * 2, 15),
            nn.Softmax(-1)
        )
        self.hp_head = nn.Sequential(
            nn.Linear(pool_size * 2, 60),###-30到30
            nn.Softmax(-1)
        )
        ##辅助值
        ##(本方)角色重要程度. 若最先死亡, 重要度=0; 第二个=0.5, 最后一个等于1.
        ##对局回合数. 一条长15的one-hot向量.
        ##终局血差(本方视角). 一条长30的one-hot向量.
        #self.auxiliary
    def forward(self, x):
        pi, v , imp, r ,hp = self.predict(x)
        return torch.exp(pi), v
    def predict(self, x):
        """
        返回LogSoftmax.用于训练
        """
        x = self.encoder(x)
        x = self.hid(x)
        pi = self.policy_head(x)
        
        pooled = self.pool(x)
        v = self.value_head(pooled)
        imp = self.imp_head(pooled)
        round = self.round_head(pooled)
        hp = self.hp_head(pooled)
        
        return pi, v, imp, round, hp

def onehot(index, classes_num):
    return torch.eye(classes_num)[index,:]


class PrinceTrainer(Trainer):
    def __init__(self, mcts: MCTS, checkpoint_root) -> None:
        super().__init__(mcts, checkpoint_root)
        self.dataset = PrinceDataset([])
    def episode(self, g: Game, sims):
        g = g.clone()
        examples = []
        obser = self.algo.obs
        death_order = {
            1:[],2:[]
        }
        while not g.terminated():
            with torch.no_grad():
                m = self.algo.search(g, 1, sims)
            pds = g.g._getpds(g.mover)
            do = death_order[g.mover]
            for i, c in enumerate(pds.char):
                if c.hp <= 0:
                    if i not in do:
                        do.append(i)
            state = obser.observe(g.g, g.mover)
            example = [g.mover, state , self.algo.pi]
            examples.append(example)
            pi = self.algo.pi
            pi = np.array(pi)
            if np.sum(pi) > 1:
                pi = pi / np.sum(pi)###缩小浮点误差
            move = np.random.choice(len(pi), p = pi)
            move = POSSIBLE_MOVES[move]
            ins = g.getIns(g.mover, move)
            g.proceed(ins, False, self.algo.callback)
        dataset = []
        winner = g.winner
        hp_diff = 0
        rounds = g.g.history['rounds']
        if winner < 0:
            hp1 = 0
            for c in g.g.p1.char:
                hp1 += c.hp
            hp2 = 0
            for c in g.g.p2.char:
                hp2 += c.hp
            hp_diff = hp1 - hp2
            if hp1 > hp2:
                winner = 1
            else:
                winner = 2
        do1 = torch.zeros(3)
        do2 = torch.zeros(3)
        imp = 0
        for d in death_order[1]:
            do1[d] = imp
            imp += 0.5
        imp = 0
        for d in death_order[2]:
            do2[d] = imp
            imp += 0.5
        hp1 = 30 + hp_diff
        hp2 = 30 - hp_diff
        
        rV = rounds###标签即可.
        for mover, state, pi in examples:
            #if winner < 0:
            #    dataset.append( (state,[pi,-1]) )
            if mover == 1:
                imp = do1
                hp = hp1
                r = rV
            else:
                imp = do2
                hp = hp2
                r = rV
            if mover == winner:
                dataset.append( (state, [pi,1 , imp,r, hp]) )
            else:
                dataset.append( (state,[pi,-1, imp, r, hp]) )
        return dataset
    def learn(self, trainset: PrinceDataset):
        self.algo.net.train()
        lr = self.lr()
        net = self.algo.net
        net:PrinceNet
        loader = DataLoader(trainset, 128, shuffle = True)
        vloss = nn.MSELoss()
        crossLoss = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(net.parameters(),lr = lr)
        for epoch in range(10):
            for i, (inputs, labels) in enumerate(loader):
                if inputs.size()[0] <= 1:
                    continue
                pis, vs = labels['pi'], labels['v']
                imps, rs, hps = labels['importancy'],labels['rounds'], labels['hp_diff']
                inputs = inputs.to(DEVICE)
                pis = pis.float().to(DEVICE)
                vs = vs.float().to(DEVICE)
                imps = imps.float().to(DEVICE)
                rs = rs.to(DEVICE)
                hps = hps.to(DEVICE)
                o_pis, o_vs, o_imps, o_rs, o_hps = net.predict(inputs)
                
                optimizer.zero_grad()
                loss = vloss(o_vs.flatten(), vs) + self.piloss(o_pis, pis) + 0.05*(\
                        crossLoss(o_rs, rs) + crossLoss(o_hps, hps) + vloss(o_imps, imps))
                loss.backward()
                optimizer.step()
                self.loss.append(loss.detach().cpu().item())
        pass