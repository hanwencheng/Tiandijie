import unittest
from primitives.Context import Context
from primitives.Action import ActionTypes
from state.apply_action import apply_action
# from primitives.formation.formations import Formations
# from primitives.Action import Action
# from calculation.PathFinding import bfs_move_range


class TestHero(unittest.TestCase):
    def test_hero(self):
        game_context = Context()

        game_context.load_buffs()

        game_context.init_formation()

        game_context.init_battlemap("jiejiehuanjing")

        game_context.init_game_heroes()

        game_context.init_heroes_position()

        game_context.battlemap.display_map()

        actor1 = game_context.get_heroes_by_player_id(0)[0]
        actor2 = game_context.get_heroes_by_player_id(1)[0]
        # from calculation.OtherlCalculation import (
        #     calculate_fix_heal,
        #     calculate_reset_hero_actionable
        # )
        from calculation.TalentEffect import TalentEffects

        actor1.reset_actionable(context=game_context)
        game_context.get_enemies_in_cross_range(actor1, 3)
        # test_action

        # from calculation.attribute_calculator import get_attack, get_defense
        test_actions = []
        for action in actor1.actionable_list:
            if action.type == ActionTypes.NORMAL_ATTACK:
                test_actions.append(action)

        test_action = test_actions[0]
        print(test_action.targets[0].current_life)
        apply_action(game_context, test_action)
        TalentEffects.take_effect_of_linghaishutao(actor1, actor2, game_context, actor1.temp.talent)
        game_context.battlemap.display_map()
