from __future__ import annotations

from random import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from primitives.Action import Action

from calculation.attribute_calculator import *
from primitives.hero import Hero



def calculate_fix_heal(
    heal, actor_instance: Hero, target_instance: Hero, context: Context
):
    defender_fix_heal_reduction = get_fixed_heal_reduction_modifier(
        target_instance, actor_instance, context
    )
    target_instance.take_healing(heal * defender_fix_heal_reduction)


def calculate_reset_hero_actionable(
    actor_instance: Hero, target_instance: Hero, context: Context
):
    target_instance.reset_actionable()
