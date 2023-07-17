import sys
sys.path.append('..')
from src.core.GameInstance import apply_react, reaction, GameInstance
from src.core.GameState import Location, Aura, GameState, Box
from src.game import activate
b1 = Box(['Diluc','Diluc','Diluc'],[])
b2 = Box(['Diluc','Diluc','Diluc'],[])
state = GameState(b1,b2)
state = activate(state)
g = GameInstance(state)

from src.core.Event import *
fake_event = Event(-1,-1,-1)

cb = lambda x: fake_event
g._issue(Over(1,-1,1, EndPhase(0,-1,1)),callback = cb)

import pickle
def test(g):
    #g = GameInstance(g.export())
    g = pickle.loads(pickle.dumps(g))
    #g = g.clone()
    target = g.p1.char[0].loc
    attacker = g.p2.char[0].loc
    dmg = damage(attacker, target, DMGType.pyro, 4)
    g._issue(DMG(g.nexteid(),-1,1,[dmg]),None)
    #assert g.p1.char[0].hp <= 0

from time import time
from timeit import timeit
start = time()

for i in range(1000):
    test(g)
    #pickle.loads(pickle.dumps(g))

now = time()

print("average time cost = ", (now-start), 'ms')

#print("average time cost = ", timeit('test(g)',number = 1000), 's')