from calculation.attribute_calculator import *


def calculate_fix_heal(
        heal, actor_instance: Hero, target_instance: Hero, context: Context
):
    defender_fix_heal_reduction = get_fixed_heal_reduction_modifier(
        target_instance, actor_instance, context
    )
    target_instance.take_healing(heal * defender_fix_heal_reduction)
