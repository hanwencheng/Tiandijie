from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from primitives.Action import Action
    from primitives import Context


def apply_move(action: Action, context: Context):
    actor = action.actor
    actor.update_position(action.move_point)


def apply_additional_move(action: Action, context: Context):
    actor = action.actor
    actor.update_position(action.additional_move)


def apply_additional_skill(action: Action, context: Context):
    actor = context.get_last_action().actor


def apply_heal(action: Action, context: Context):
    pass


def apply_summon(action: Action, context: Context):
    pass


def apply_teleport(action: Action, context: Context):
    pass


def apply_self(action: Action, context: Context):
    pass
