from typing import List, Any
from typing import TYPE_CHECKING


from primitives.Action import Action
if TYPE_CHECKING:
    from primitives.Context import Context
from primitives.effects.Event import EventTypes
from primitives.effects.EventListener import EventListener
from calculation.Range import calculate_if_targe_in_diamond_range
from primitives.hero.Hero import Hero
from random import random

skill_related_events = [
    EventTypes.skill_start,
    EventTypes.skill_end,
    EventTypes.damage_start,
    EventTypes.damage_end,
    EventTypes.skill_single_damage_start,
    EventTypes.skill_single_damage_end,
    EventTypes.skill_range_damage_start,
    EventTypes.skill_range_damage_end,
    EventTypes.under_damage_start,
    EventTypes.under_damage_end,
    EventTypes.under_skill_single_damage_start,
    EventTypes.under_skill_single_damage_end,
    EventTypes.under_skill_range_damage_start,
    EventTypes.under_skill_range_damage_end,
]


class EventListenerContainer:
    def __init__(self, event_listener: EventListener, instance_self: Any):
        self.event_listener = event_listener
        self.instance_self = instance_self


def event_listener_calculator(
    actor_instance: Hero,
    counter_instance: Hero or None,
    event_type: EventTypes,
    context,
):
    if actor_instance.is_alive is False:
        return
    event_listener_containers: List[EventListenerContainer] = []
    current_action: Action = context.get_last_action()
    if current_action is None:
        return
    # Calculated Buffs
    for buff in actor_instance.buffs:
        buff_event_listeners: List[EventListener] = buff.temp.event_listeners
        for event_listener in buff_event_listeners:
            if event_listener.event_type == event_type:
                event_listener_containers.append(
                    EventListenerContainer(event_listener, buff)
                )

    # Calculated FieldBuffs
    for field_buff in context.fieldbuffs_temps.values():
        target_instance = context.get_hero_by_id(field_buff.caster_id)
        if (
            target_instance
            and target_instance.get_field_buff_by_id(field_buff.id)
            and calculate_if_targe_in_diamond_range(
                actor_instance, target_instance, field_buff.buff_range
            )
        ):
            field_buff_event_listeners: List[EventListener] = field_buff.event_listeners
            for event_listener in field_buff_event_listeners:
                if event_listener.event_type == event_type:
                    event_listener_containers.append(
                        EventListenerContainer(event_listener, field_buff)
                    )

    # Calculated Skills
    if event_type in skill_related_events:
        skill = current_action.skill
        if skill:
            for event_listener in skill.temp.event_listeners:
                if event_listener.event_type == event_type:
                    event_listener_containers.append(
                        EventListenerContainer(event_listener, skill)
                    )

    # Calculate Talents

    # Calculate Formation
    formation = context.get_formation_by_player_id(actor_instance.player_id)
    if formation is not None:
        formation_event_listeners: List[EventListener] = formation.temp.event_listeners
        for event_listener in formation_event_listeners:
            if event_listener.event_type == event_type:
                event_listener_containers.append(
                    EventListenerContainer(event_listener, formation)
                )

    # Calculate Passives

    # re-order the event listeners by priority in accumulated_event_listeners
    event_listener_containers.sort(key=lambda x: x.listener.priority)

    for event_listener_container in event_listener_containers:
        multiplier = event_listener_container.event_listener.requirement(
            actor_instance,
            counter_instance,
            context,
            event_listener_container.instance_self,
        )
        if multiplier > 0 and random() < multiplier:
            event_listener_container.event_listener.listener_effects(
                actor_instance,
                counter_instance,
                context,
                event_listener_container.instance_self,
            )


def death_event_listener(
    actor_instance: Hero,
    counter_instance: Hero or None,
    event_type: EventTypes,
    context,
):
    # 统计自身是否带禁止复生buff，以及target.died_once是否为False，再统计自己是否有复生modifier：int 根据modifier的值来判断复活后的血量， died_once = True
    pass
