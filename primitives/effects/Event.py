import enum


class EventTypes(enum.Enum):
    move_start = 'move_start'
    move = 'move'
    move_end = 'move_end'

    action_start = 'action_start'
    # damage
    damage_start = 'damage_start'
    damage = 'damage'
    damage_end = 'damage_end'
    # battle
    battle_start = 'battle_start'
    battle = 'battle'
    battle_end = 'battle_end'
    # normal_attack
    normal_attack_start = 'normal_attack_start'
    normal_attack = 'normal_attack'
    normal_attack_end = 'normal_attack_end'
    # protect
    protect_start = 'protect_start'
    protect_end = 'protect_end'
    # critical_damage
    critical_damage_start = 'critical_damage_start'
    critical_damage = 'critical_damage'
    critical_damage_end = 'critical_damage_end'
    # heal
    heal_start = 'heal_start'
    heal = 'heal'
    heal_end = 'heal_end'
    # summon
    summon_start = 'summon_start'
    summon = 'summon'
    summon_end = 'summon_end'
    # self
    self_start = 'self_start'
    self = 'self'
    self_end = 'self_end'
    # pass
    pass_start = 'pass_start'
    pass_end = 'pass_end'
    # counterattack
    counterattack_start = 'counterattack_start'
    counterattack = 'counterattack'
    counterattack_end = 'counterattack_end'

    action_end = 'action_end'

    # skill for self
    skill_for_self_start = 'skill_for_self_start'
    skill_for_self_end = 'skill_for_self_end'
    # skill for terrain
    skill_for_terrain_start = 'skill_for_terrain_start'
    skill_for_terrain_end = 'skill_for_terrain_end'
    # skill for partners
    skill_for_partner_start = 'skill_for_partner_start'
    skill_for_partner_end = 'skill_for_partner_end'
    # range_damage
    skill_range_damage_start = 'range_damage_start'
    skill_range_damage_end = 'range_damage_end'
    # single_damage
    skill_single_damage_start = 'single_damage_start'
    skill_single_damage_end = 'single_damage_end'

    partner_action_start = 'partner_action_start'
    partner_action = 'partner_action'
    partner_action_end = 'partner_action_end'

    partner_battle_start = 'partner_battle_start'
    partner_battle = 'partner_battle'
    partner_battle_end = 'partner_battle_end'

    enemy_action_start = 'enemy_action_start'
    enemy_action = 'enemy_action'
    enemy_action_end = 'enemy_action_end'

    enemy_battle_start = 'enemy_battle_start'
    enemy_battle = 'enemy_battle'
    enemy_battle_end = 'enemy_battle_end'

    hero_death = 'hero_death'
