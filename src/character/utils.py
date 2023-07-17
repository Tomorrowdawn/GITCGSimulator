import src.character.chars as chr
###对这个模块执行反射函数即可.
from src.character.character import Character

def name2char(name:str)->Character:
    #return eval('chr.'+name,globals())()###这居然是最快的
    #return chr.Diluc()
    return getattr(chr, name)()
    pass