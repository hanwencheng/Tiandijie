import unittest
from primitives.Context import Context
from primitives.formation.formations import Formations
from primitives.Action import Action
from primitives.Action import ActionTypes
from calculation.PathFinding import bfs_move_range
from state.apply_action import apply_action


class TestHero(unittest.TestCase):
    def test_hero(self):
        game_context = Context()

        game_context.load_buffs()

        game_context.init_formation()

        game_context.init_battlemap("jiejiehuanjing")

        game_context.init_game_heroes()

        game_context.init_heroes_position()

        game_context.battlemap.display_map(game_context)

        game_context.get_heroes_by_player_id(0)[0].initialize_movable_range(game_context.battlemap, game_context.heroes)
        game_context.get_heroes_by_player_id(0)[0].initialize_actionable_hero(game_context.heroes)

        from calculation.attribute_calculator import get_attack, get_defense

        test_actions = []
        for action in game_context.get_heroes_by_player_id(0)[0].actionable_list:
            if action.type == ActionTypes.NORMAL_ATTACK:
                test_actions.append(action)

        test_action = test_actions[0]
        print(test_action.targets[0].current_life)
        apply_action(game_context, test_action)
        print(test_action.targets[0].current_life)
        game_context.add_action(test_action)

        get_attack = get_defense(game_context.get_heroes_by_player_id(0)[0], game_context.get_heroes_by_player_id(1)[0], True, game_context)
        print(get_attack)
