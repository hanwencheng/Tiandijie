from state.setup import setup_context
from state.apply_action import apply_action


class State(pyspiel.State):
    def __int__(self):
        self._cur_player = 0
        self._player0_score = 0.0
        self._player1_score = 0.0
        self._isterminal = False
        self.context = setup_context()

    def _apply_action(self, action):
        apply_action(self.context, action)

    def returns(self):
        pass

    def _legal_actions(self, player):   # 返回可执行的操作
        legal_actions = []

        action = self.context.get_last_action()
        if action.additional_move > 0:
            legal_actions.append(action.additional_move)

        if action.additional_skill is not None:
            legal_actions.append(action.additional_skill)

        if action.additional_action is not None:
            legal_actions.append(action.additional_action)

        if len(legal_actions) == 0:
            for hero in self.context.heroes:
                if hero.actionable:
                    legal_actions.append(hero.movable_range)
                    legal_actions.append(hero.attack_range)


        return legal_actions

