from __future__ import annotations
from collections import Counter
from typing import List, TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from primitives.buff.buffs import BuffTemps
    from primitives import Action
    from primitives.formation.Formation import Formation
    from primitives.buff.BuffTemp import BuffTemp, BuffTypes
    from primitives.hero import Hero

from calculation.Range import calculate_square_area, calculate_diamond_area


class Context:
    def __init__(self):
        self.heroes: List[Hero] = []
        self.formation: List[Formation] = []
        self.actions: List[Action] = []
        self.harm_buffs_temps: Dict[str, BuffTemp] = {}
        self.benefit_buffs_temps: Dict[str, BuffTemp] = {}
        self.all_buffs_temps: Dict[str, BuffTemp] = {}

    def add_action(self, action):
        self.actions.append(action)

    def get_last_action(self) -> Action:
        if self.actions:
            return self.actions[-1]
        else:
            return None  # Return None if there are no actions

    def get_partners_in_diamond_range(self, hero: Hero, range_value: int) -> List[Hero]:
        base_position = hero.position
        positions_list_in_range = calculate_diamond_area(base_position, range_value)
        return [
            hero
            for hero in self.heroes
            if hero.position in positions_list_in_range
            and hero.player_id == hero.player_id
        ]

    def get_enemies_in_square_range(self, hero: Hero, range_value: int) -> List[Hero]:
        base_position = hero.position
        positions_list_in_range = calculate_square_area(base_position, range_value)
        return [
            hero
            for hero in self.heroes
            if hero.position in positions_list_in_range
            and hero.player_id != hero.player_id
        ]

    def load_buffs(self):
        from primitives.buff.buffs import BuffTemps

        all_buffs = {}
        harm_buffs = {}
        benefit_buffs = {}
        for buff in BuffTemps:
            all_buffs[buff.value.id] = buff.value
            if buff.value.buff_type == BuffTypes.Harm:
                harm_buffs[buff.value.id] = buff.value
            elif buff.value.buff_type == BuffTypes.Benefit:
                benefit_buffs[buff.value.id] = buff.value
        self.all_buffs_temps = all_buffs
        self.harm_buffs_temps = harm_buffs
        self.benefit_buffs_temps = benefit_buffs

    def init_heroes(self, heroes: List[Hero]):
        self.heroes = heroes

    def get_current_player_id(self) -> int:
        return self.get_last_action().player_id

    def get_counter_player_id(self) -> int:
        return 1 - self.get_current_player_id()

    def get_formation_by_player_id(self, player_id: int) -> Formation:
        return [
            formation
            for formation in self.formation
            if formation.player_id == player_id
        ][0]

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
                requirements = (
                    formation_temp.activation_requirements
                )  #  [{'profession': Professions.SORCERER}, {'profession': Professions.GUARD}]

                # Remove the current hero from the check to only consider other heroes
                other_heroes = [h for h in heroes if h != hero]

                def is_requirement_satisfied(req, check_heroes):
                    key = next(iter(req))
                    return sum(
                        getattr(h.temp, key, None) == req[key] for h in check_heroes
                    )

                # Count how many times each requirement appears
                req_counts = Counter(
                    str(req) for req in requirements
                )  # Convert dict to str for immutability

                # Check each unique requirement against the number of heroes that satisfy it
                satisfied_counts = Counter(
                    {
                        str(req): is_requirement_satisfied(req, other_heroes)
                        for req in requirements
                    }
                )
                # Ensure for each requirement type, the number of heroes that satisfy it meets or exceeds the requirement count
                if all(
                    satisfied_counts[str(req)] >= count
                    for req, count in req_counts.items()
                ):
                    self.formation = Formation(hero.player_id, formation_temp)
                    self.formation.active_formation()

    def get_harm_buff_temp_by_id(self, buff_temp_id: str) -> BuffTemp:
        return self.harm_buffs_temps[buff_temp_id]

    def get_buff_by_id(self, buff_id: str) -> BuffTemp:
        return self.all_buffs_temps[buff_id]
