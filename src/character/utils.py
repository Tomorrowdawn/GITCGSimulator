import src.character as chr
###对这个模块执行反射函数即可.
from src.character.character import Character

def name2char(name:str)->Character:
    return eval('chr.'+name)()
    pass