import sys
sys.path.append('..')
from src.game import Game
from src.core.GameInstance import GameInstance,PlayerInstance,Aura
from src.core.Event import *
import time
from src.character.char1 import GlacialWaltz
from src.core.EventManage import EventHub

class Searcher:
    WIN_SCORE = 1000
    def __init__(self,player = 1) -> None:
        self.nodes = 0
        self.start_time = 0
        self.player_id = player
        self.remain_depth = 0
        self.searching = False
        #self.pv_line = []
        self.time_limit = 5
    def _scores(self, p:PlayerInstance):
        hp_scores = 0
        aura_scores = 0
        summon_scores = 0
        energy_scores = 0
        dice_scores = 0
        buff_scores = 0
        if not p.history['endround']:
            dice_scores = p.dice.num() * 20
        else:
            dice_scores = 0
        for c in p.char:
            if c.hp > 0:
                hp_scores += c.hp * 10
                energy_scores += c.energy
                if c.aura != Aura.empty:
                    aura_scores += -10
        for b in p.buff:
            if isinstance(b, GlacialWaltz) and len(p.getalives()) > 1:
                buff_scores += b.usage * 2 * 7
        for s in p.summon:
            summon_scores += s.dvalue * s.usage * 7
        return hp_scores + aura_scores + summon_scores + buff_scores + dice_scores + energy_scores
    def val(self, g:Game):
        if g.terminated():
            if g.g.history['winner'] == g.g.history['mover']:
                return Searcher.WIN_SCORE
            else:
                return -Searcher.WIN_SCORE
        gi = g.g
        player_id = g.mover
        active_player = gi._getpds(player_id)
        oppo = gi._getpds(3-player_id)
        return self._scores(active_player) - self._scores(oppo)
    def callback(self, g:GameInstance,event, event_set, event_queue):
        if isinstance(event, Death) and g.history['phase'] == 'deathswitch':
            active = g.getactive(event.player_id)
            #temp = g.clone()
            best = -10000
            best_s = None
            for direct in (1,-1):
                s = Switch(g.nexteid(), event.eid, event.player_id, active, direct)
                game = Game()
                game.g = g.clone()
                eh = EventHub(event_set + [s] + event_queue)
                eh.checkout(game.g, self.callback)
                if self.searching:
                    val = self._alphabeta(game, -Searcher.WIN_SCORE, Searcher.WIN_SCORE, self.remain_depth)
                else:
                    self.searching = True
                    #self.remain_depth = 7
                    val = self._alphabeta(game, -Searcher.WIN_SCORE, Searcher.WIN_SCORE, 7)
                    self.searching = False
                if event.player_id != game.mover:
                    val = -val
                if val > best:
                    best = val
                    best_s = s
            return best_s
        else:
            return Event(-1,-1,-1)
    def _alphabeta(self, g:Game , alpha, beta, depth):
        self.remain_depth = depth - 1
        self.nodes += 1
        #if time.time() - self.start_time > self.time_limit:
        #    return self.val(g)
        if g.terminated():
            return self.val(g)
        if depth <= 0:
            return self.val(g)
        #if depth <= 2 and self.val(g) + 5 < alpha:
        #    depth -= 1
        #if depth % 2 == 0:
            #ng = g.clone()
        #    pds = g.g._getpds(g.g.mover)
        #    omnibackup = pds.dice.dice.omni
        #    pds.dice.dice.omni -= 2
        #    if pds.dice.dice.omni < 0:
        #        pds.dice.dice.omni = 0
        #    val = self._alphabeta(g, alpha,beta,depth - 3)##自损裁剪
        #    pds.dice.dice.omni = omnibackup
        #    if val >= beta:
        #        return beta
        def moves():
            for move in ['burst', 'skill','na','switch next','switch previous','end round']:
                ins = g.getIns(g.mover, move)
                if ins is not None:
                    yield ins
        for move in moves():
            ng = g.proceed(move,new_game=True,callback=self.callback)
            if ng.mover == g.mover:
                val = self._alphabeta(ng, alpha, beta, depth - 1)
            else:
                val = -self._alphabeta(ng, -beta, -alpha, depth - 1)
            #print("move = ",move)
            #print("val = ",val)
            if val >= beta:
                #self.fail_soft[self.remain_depth] += 1
                return beta
            if val > alpha:
                alpha = val
        return alpha
    def _search(self,g,depth):
        self.nodes += 1
        self.remain_depth = depth - 1
        def moves():
            for move in ['burst', 'skill','na', 'switch next','switch previous','end round']:
                ins = g.getIns(g.mover, move)
                if ins is not None:
                    yield ins
        scores = []
        actions = []
        beta = Searcher.WIN_SCORE + 1
        alpha = -Searcher.WIN_SCORE - 1
        for move in moves():
            actions.append(move)
            ng = g.proceed(move,new_game = True, callback = self.callback)
            if g.mover == ng.mover:
                val = self._alphabeta(ng, alpha, beta,depth - 1)
            else:
                val = -self._alphabeta(ng,-beta, -alpha,depth - 1)
            scores.append(val)
            if val > alpha:
                alpha = val
            if val >= beta:
                #self.fail_soft[self.remain_depth] += 1
                return actions, scores
        return actions, scores
    def search(self, g:Game, time_limit , debug = False, verbose = False, **kwargs):
        def argmax(array):
            return max(list(enumerate(array)), key=lambda x: x[1])
        self.time_limit = time_limit
        self.nodes = 0
        self.start_time = time.time()
        self.searching = True
        if debug:
            d = kwargs['depth']
            self.fail_soft = [0 for i in range(d)]
            moves, scores = self._search(g, d)
            i, score = argmax(scores)
            move = moves[i]
            #print("fail_soft:")
            #print(self.fail_soft)
        else:
            for d in range(1,20):
                #old_nodes = self.nodes
                moves, scores = self._search(g, d)
                #inc = self.nodes - old_nodes
                #print("depth = %d, search nodes %d" % (d, inc))
                i, score = argmax(scores)
                move = moves[i]
                if time.time() - self.start_time > time_limit:
                    break
        #move = g.getIns(self.player_id, move)
        #print("moves = " , moves)
        if verbose:
            print("scores = ", scores)
        self.searching = False
        if verbose:
            return move, score, d
        else:
            return move