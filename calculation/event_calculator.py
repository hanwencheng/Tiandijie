from typing import List, Any
from primitives.Action import Action
from primitives.Context import Context
from primitives.buff.Buff import Buff
from primitives.effects.Event import EventTypes
from primitives.effects.EventListener import EventListener
from primitives.hero.Hero import Hero

skill_related_events = [
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


def event_listener_calculator(actor_instance: Hero, counter_instance: Hero or None, event_type: EventTypes,
                              context: Context):
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
                event_listener_containers.append(EventListenerContainer(event_listener, buff))
    
    # Calculated Skills
    if event_type in skill_related_events:
        skill = current_action.skill
        for event_listener in  skill.temp.event_listeners:
            if event_listener.event_type == event_type:
                event_listener_containers.append(EventListenerContainer(event_listener, skill))

    # Calculate Talents

    # Calculate Formation
    formation = context.get_formation_by_player_id(actor_instance.player_id)
    if formation is not None:
        formation_event_listeners: List[EventListener] = formation.temp.event_listeners
        for event_listener in formation_event_listeners:
            if event_listener.event_type == event_type:
                event_listener_containers.append(EventListenerContainer(event_listener, formation))

    # Calculate Passives

    # re-order the event listeners by priority in accumulated_event_listeners
    event_listener_containers.sort(key=lambda x: x.listener.priority)

    for event_listener_container in event_listener_containers:
        multiplier = event_listener_container.event_listener.requirement(actor_instance, counter_instance, context, event_listener_container.instance_self)
        if round(multiplier) > 0:
            event_listener_container.event_listener.listener_effects(actor_instance, counter_instance, context,
                                                                     event_listener_container.instance_self)
