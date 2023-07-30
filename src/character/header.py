from __future__ import annotations
import sys

sys.path.extend(['..','../..'])

from src.character.character import Character
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from src.core.GameInstance import GameInstance
    
from src.core.Event import DMGType, List, damage
import src.core.Event as Event
from src.core.base import DicePattern
from src.core.Listener import Buff, Summoned, CharBuff