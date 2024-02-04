from typing import List, Any

from primitives import Action
from primitives.formation.Formation import Formation
from primitives.buff.BuffTemp import BuffTemp
from primitives.formation.FormationTemp import FormationTemp
from primitives.hero import Hero


class Context:
    def __init__(self):
        self.heroes: List[Hero] = []
        self.formation: List[Formation] = []
        self.actions: List[Action] = []
        self.harm_buffs: List[BuffTemp] = []
        self.benefit_buffs: List[BuffTemp] = []

    def add_action(self, action):
        self.actions.append(action)

    def get_last_action(self) -> Action:
        if self.actions:
            return self.actions[-1]
        else:
            return None  # Return None if there are no actions

    def get_partners_in_range(self, hero: Hero, range_value: int) -> List[Hero]:
        pass

    def init_buffs(self, harm_buffs, benefit_buffs):
        self.harm_buffs = harm_buffs
        self.benefit_buffs = benefit_buffs

    def init_heroes(self, heroes: List[Hero]):
        self.heroes = heroes

    def get_current_player_id(self) -> int:
        return self.get_last_action().player_id

    def get_formation_by_player_id(self, player_id: int) -> Formation:
        return [formation for formation in self.formation if formation.player_id == player_id][0]

    def get_heroes_by_player_id(self, player_id: int) -> List[Hero]:
        return [hero for hero in self.heroes if hero.player_id == player_id]

    def get_heroes_by_counter_player_id(self, player_id: int) -> List[Hero]:
        return [hero for hero in self.heroes if hero.player_id != player_id]

    def set_hero_died(self, hero: Hero):
        hero.is_alive = False
        self.heroes.remove(hero)

    def get_actor_by_side_in_battle(self, is_attacker: bool) -> Hero:
        current_action = self.get_last_action()
        if is_attacker:
            return current_action.actor
        else:
            return current_action.target[0]

    def get_targets_by_id(self, hero_id: str) -> List[Hero]:
        current_action = self.get_last_action()
        if current_action.is_attacker(hero_id):
            return current_action.targets
        else:
            return [current_action.actor]

    def get_hero_by_id(self, hero_id: str) -> Hero:
        return [hero for hero in self.heroes if hero.id == hero_id][0]

    def init_formation(self):
        for hero in self.heroes:
            formation_temp = hero.temp.formation_temp
            if hero.temp.has_formation:
                heroes = self.get_heroes_by_player_id(hero.player_id)
                requirements = formation_temp.activation_requirements

                def is_requirement_satisfied(req, check_heroes):
                    key = next(iter(req))
                    return any(getattr(check_hero.temp, key, None) == req[key] for check_hero in check_heroes)

                if all(is_requirement_satisfied(req, heroes) for req in requirements):
                    self.formation = Formation(hero.player_id, formation_temp)
                    self.formation.active_formation()

    def get_harm_buff_temp_by_id(self, buff_temp_id: str) -> BuffTemp:
        return [buff for buff in self.harm_buffs if buff.id == buff_temp_id][0]
