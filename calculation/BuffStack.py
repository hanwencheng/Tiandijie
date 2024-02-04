from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from primitives.buff.Buff import Buff
from typing import List
from calculation.ModifierAttributes import ModifierAttributes as ma


class BuffStack:
    def __init__(self, max_stack: int, affected_attributes: List[str]):
        self.max_stack = max_stack
        self.affected_attributes = affected_attributes


buff_max_stack = {
    "xianzui": BuffStack(3, [ma.damage_reduction_percentage, ma.damage_percentage]),
    "xiayi": BuffStack(3, [])
}


def calculate_buff_with_max_stack(buff: Buff, modifier: dict[str, float], attr_name: str):
    if buff.temp.id in buff_max_stack:
        target_buff_stack = buff_max_stack[buff.temp.id]
        max_stack = target_buff_stack.max_stack
        if attr_name in target_buff_stack.affected_attributes:
            return modifier[attr_name] * max_stack
    return modifier


def get_buff_max_stack(buff_id: str):
    return buff_max_stack[buff_id][0] if buff_id in buff_max_stack else 1
