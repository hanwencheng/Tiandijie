import enum


class EventTypes(enum.Enum):

    move_start = "move_start"
    move = "move"
    move_end = "move_end"

    action_start = "action_start"

    turn_start = "turn_start"
    turn_end = "turn_end"

    # damage
    damage_start = "damage_start"
    damage_end = "damage_end"
    under_damage_start = "under_damage_start"
    under_damage_end = "under_damage_end"
    under_magic_damage_start = "under_magic_damage_start"
    under_magic_damage_end = "under_magic_damage_end"
    # battle
    battle_start = "battle_start"
    battle_end = "battle_end"
    under_battle_start = "under_battle_start"
    under_battle_end = "under_battle_end"
    # normal_attack
    normal_attack_start = "normal_attack_start"
    normal_attack_end = "normal_attack_end"
    under_normal_attack_start = "under_normal_attack_start"
    under_normal_attack_end = "under_normal_attack_end"
    # protect
    protect_start = "protect_start"
    protect_end = "protect_end"
    # critical_damage
    critical_damage_start = "critical_damage_start"
    critical_damage_end = "critical_damage_end"
    under_critical_damage_start = "under_critical_damage_start"
    under_critical_damage_end = "under_critical_damage_end"
    # heal
    heal_start = "heal_start"
    heal_end = "heal_end"
    under_heal_start = "under_heal_start"
    under_heal_end = "under_heal_end"
    # summon
    summon_start = "summon_start"
    summon_end = "summon_end"
    # self
    self_start = "self_start"
    self_end = "self_end"
    # pass
    pass_start = "pass_start"
    pass_end = "pass_end"
    # counterattack
    counterattack_start = "counterattack_start"
    counterattack_end = "counterattack_end"
    under_counterattack_start = "under_counterattack_start"
    under_counterattack_end = "under_counterattack_end"
    # teleport
    teleport_start = "teleport_start"
    teleport_end = "teleport_end"

    action_end = "action_end"

    # all_skill
    skill_start = "skill_start"
    skill_end = "skill_end"
    # skill for self
    skill_for_self_start = "skill_for_self_start"
    skill_for_self_end = "skill_for_self_end"
    # skill for terrain
    skill_for_terrain_start = "skill_for_terrain_start"
    skill_for_terrain_end = "skill_for_terrain_end"
    # skill for partners
    skill_for_partner_start = "skill_for_partner_start"
    skill_for_partner_end = "skill_for_partner_end"
    # range_damage
    skill_range_damage_start = "range_damage_start"
    skill_range_damage_end = "range_damage_end"
    under_skill_range_damage_start = "under_skill_range_damage_start"
    under_skill_range_damage_end = "under_skill_range_damage_end"
    # single_damage
    skill_single_damage_start = "single_damage_start"
    skill_single_damage_end = "single_damage_end"
    under_skill_single_damage_start = "under_skill_single_damage_start"
    under_skill_single_damage_end = "under_skill_single_damage_end"

    partner_action_start = "partner_action_start"
    partner_action_end = "partner_action_end"

    partner_battle_start = "partner_battle_start"
    partner_battle_end = "partner_battle_end"

    enemy_action_start = "enemy_action_start"
    enemy_action_end = "enemy_action_end"

    enemy_battle_start = "enemy_battle_start"
    enemy_battle_end = "enemy_battle_end"

    enemy_skill_start = "enemy_skill_start"
    enemy_skill_end = "enemy_skill_end"

    # buff
    buff_start = "buff_start"
    buff_end = "buff_end"

    hero_death = "hero_death"

    # double_attack
    double_attack_start = "double_attack_start"
    double_attack_end = "double_attack_end"
    under_double_attack_start = "under_double_attack_start"
    under_double_attack_end = "under_double_attack_end"
