from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from primitives.Context import Context
    from basics import Position
    from SkillTemp import SkillTemp


class Skill:
    def __int__(self, action_position: Position or None, skill_temp: SkillTemp):
        self.action_position = action_position
        self.temp = skill_temp
