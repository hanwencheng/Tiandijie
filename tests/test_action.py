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

        # actor1 = game_context.get_heroes_by_player_id(0)[0]
        # actor2 = game_context.get_heroes_by_player_id(1)[0]
        #

        from main import State

        game_state = State(game_context)
        print(f"现在是玩家{game_state._cur_player}的行动")
        legal_actions = game_state._legal_actions(game_state._cur_player)
        test_action = legal_actions[2]
        test_actor = test_action.actor
        for action in legal_actions:
            if action.actor.id == "mohuahuangfushen0" and action.skill and action.skill.temp.id == "leiyinwanyu" and len(action.targets) >= 3 and action.move_point == (4, 8):
                test_action = action
                test_actor = action.actor
                break
        print("--------------")
        print_list = []
        for target in test_action.targets:
            print_list.append(target.id)
        print("作用到了这些人物：", print_list)
        print("--------------")
        print("己方最终位置：", test_action.action_point)
        print("--------------")
        print("敌人的初始血量：")

        for actor in game_context.get_heroes_by_player_id(1):
            print(actor.id, "的初始血量：",  actor.current_life)

        game_state._apply_action(test_action)

        print("--------------")
        print("action1的之后的血量")
        for actor in game_context.get_heroes_by_player_id(1):
            print(actor.id, "action后的血量：", actor.current_life)
        game_context.battlemap.display_map()
        print("--------------")
        print("现在技能转换成这样")
        for skill in test_actor.enabled_skills:
            print(skill.temp.id, skill.cool_down)
        print("--------------")
        print(f"现在是玩家{game_state._cur_player}的行动")
        legal_actions = game_state._legal_actions(game_state._cur_player)
        print(f"有{len(legal_actions)}种行动方案")
        print("其中有技能的分别是")
        for action in legal_actions:
            if action.skill:
                print(action.skill.temp.id, "技能对象为：", action.targets[0].id)
            if action.skill and action.skill.temp.id == "tianshanluanhun" and action.targets[0].id == "fuyayu1":
                test_action = action
                test_actor = action.actor
        print("--------------")
        print("选一个天闪乱魂使用")
        print("适用对象为：", test_action.targets[0].id)
        game_state._apply_action(test_action)
        print(test_action.targets[0].id, "最终血量为：", test_action.targets[0].current_life)
        print("-------展示整个action后的map-------")
        game_context.battlemap.display_map()
        print("--------------")
        print(f"现在是玩家{game_state._cur_player}的行动")
        legal_actions = game_state._legal_actions(game_state._cur_player)
        print(f"有{len(legal_actions)}种行动方案")
        for action in legal_actions:
            if action.actor.id == "huoyong1" and action.skill and action.skill.temp.id == "huntiantuixing" and action.move_point == action.initial_position:
                test_action = action
                test_actor = action.actor
                print("已查找到可用action")
        game_state._apply_action(test_action)
        print("查看下是否正常获得buff")
        for buff in test_actor.buffs:
            print(buff.temp.id)
        print("查看下skill是否正常进入cd")
        for skill in test_actor.enabled_skills:
            print(skill.temp.id, skill.cool_down)
        print("--------------")
        print(f"现在是玩家{game_state._cur_player}的行动")
        legal_actions = game_state._legal_actions(game_state._cur_player)
        print(f"有{len(legal_actions)}种行动方案")
        print("其中有技能的分别是")
        for action in legal_actions:
            if action.skill and action.skill.temp.id == "tianshuangxuewu" and action.move_point == action.initial_position:
                test_action = action
                test_actor = action.actor
                print("已查找到可用action")
        game_state._apply_action(test_action)
        print("--------------")
        print("查看下skill是否正常进入cd")
        for skill in test_actor.enabled_skills:
            print(skill.temp.id, skill.cool_down)
        print("查看下是否正常消耗buff")
        for buff in test_actor.buffs:
            print(buff.temp.id)
        print("-------展示整个action后的map-------")
        game_context.battlemap.display_map()
        print(f"现在是玩家{game_state._cur_player}的行动")
