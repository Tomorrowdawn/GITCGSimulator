import sys
sys.path.append('..')
from src.game import Game
from src.core.GameInstance import GameInstance,PlayerInstance,Aura
from src.core.Event import *
import time
from src.character.char1 import GlacialWaltz

class Searcher:
    WIN_SCORE = 1000
    def __init__(self,player = 1) -> None:
        self.nodes = 0
        self.start_time = 0
        self.player_id = player
    def _scores(self, p:PlayerInstance):
        hp_scores = 0
        aura_scores = 0
        summon_scores = 0
        energy_scores = 0
        dice_scores = 0
        buff_scores = 0
        if not p.history['endround']:
            dice_scores = p.dice.num() // 3 * 2
        else:
            dice_scores = 0
        for c in p.char:
            if c.hp > 0:
                hp_scores += c.hp
                energy_scores += c.energy * 0.4
                if c.aura != Aura.empty:
                    aura_scores += -1
        for b in p.buff:
            if isinstance(b, GlacialWaltz):
                buff_scores += b.usage * 2 * 0.7
        for s in p.summon:
            summon_scores += s.dvalue * s.usage * 0.5
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
            return Switch(g.nexteid(), event.eid, event.player_id, active, 1)
        else:
            return Event(-1,-1,-1)
    def _alphabeta(self, g:Game , alpha, beta, depth):
        self.nodes += 1
        if time.time() - self.start_time > self.time_limit:
            return self.val(g)
        if g.terminated():
            return self.val(g)
        if depth <= 0:
            return self.val(g)
       # if depth <= 2 and self.val(g) + 5 < alpha:
        #    depth -= 1
        def moves():
            for move in ['skill','na','switch next','switch previous','burst','end round']:
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
                return beta
            if val > alpha:
                alpha = val
        return alpha
    def _search(self,g,depth):
        def moves():
            for move in ['skill','na','switch next','switch previous','burst','end round']:
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
                return actions, scores
        return actions, scores
    def search(self, time_limit, g:Game, debug = False, **kwargs):
        def argmax(array):
            return max(list(enumerate(array)), key=lambda x: x[1])
        self.time_limit = time_limit
        self.nodes = 0
        self.start_time = time.time()
        if debug:
            d = kwargs['depth']
            moves, scores = self._search(g, d)
            i, score = argmax(scores)
            move = moves[i]
        else:
            for d in range(1,100):
                moves, scores = self._search(g, d)
                i, score = argmax(scores)
                move = moves[i]
                if time.time() - self.start_time > time_limit:
                    break
        #move = g.getIns(self.player_id, move)
        #print("moves = " , moves)
        print("scores = ", scores)
        return move, score, d