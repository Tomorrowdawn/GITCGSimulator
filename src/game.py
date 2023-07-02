from src.core.GameState import GameState, GameInstance
class Game:
    def __init__(self):
        self.gs = None
        pass
    def load(self, gs:GameState):
        self.gs = gs.clone()
        pass
    def proceed(self, action)->"Game":
        NewGame = Game()
        GI = GameInstance(self.gs)
        
        ###在GI中执行具体逻辑
        
        ###
        
        ###
        
        gs = GI.export()
        NewGame.load(gs)
        return NewGame
    
    @property
    def mover(self):
        pass
    
    @property
    def phase(self):
        pass
    
    @property
    def state(self):
        pass
    
    @property
    def valids(self):
        pass