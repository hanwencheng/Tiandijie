from __future__ import annotations

import random
from collections import Counter
from typing import List, TYPE_CHECKING, Dict
from primitives.map.BattleMap import BattleMap

if TYPE_CHECKING:
    from primitives.buff.buffs import BuffTemps
    from primitives.fieldbuff.fieldbuffs import FieldBuffsTemps
    from primitives import Action
    from primitives.formation.Formation import Formation
    from primitives.buff.BuffTemp import BuffTemp
    from primitives.fieldbuff.FieldBuffTemp import FieldBuffTemp
from primitives.equipment.Equipments import Equipments
from primitives.hero.Hero import Hero
from primitives.hero.heroes import HeroeTemps
from primitives.buff.BuffTemp import BuffTypes
from primitives.Stone import Stones
from primitives.skill.Skill import Skill
from primitives.skill.skills import Skills
from primitives.map.maps import Maps

from calculation.Range import (
    calculate_square_area,
    calculate_diamond_area,
    calculate_cross_area,
)

from primitives.map.Terrain import Terrain

type TerrainMap = List[List[Terrain]]


class Context:
    def __init__(self):
        self.heroes: List[Hero] = []
        self.formation: List[Formation] = []
        self.actions: List[Action] = []
        self.harm_buffs_temps: Dict[str, BuffTemp] = {}
        self.benefit_buffs_temps: Dict[str, BuffTemp] = {}
        self.fieldbuffs_temps: Dict[str, FieldBuffTemp] = {}
        self.all_buffs_temps: Dict[str, BuffTemp] = {}
        self.battlemap = None

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
            if hero.position in positions_list_in_range and hero.player_id == hero.player_id
        ]

    def get_all_partners(self, hero: Hero) -> List[Hero]:
        return [partner_hero for partner_hero in self.heroes if partner_hero.player_id == hero.player_id]

    def get_enemies_in_diamond_range(self, hero: Hero, range_value: int) -> List[Hero]:
        base_position = hero.position
        positions_list_in_range = calculate_diamond_area(base_position, range_value)
        return [
            hero
            for hero in self.heroes
            if hero.position in positions_list_in_range and hero.player_id != hero.player_id
        ]

    def get_enemies_in_square_range(self, hero: Hero, range_value: int) -> List[Hero]:
        base_position = hero.position
        positions_list_in_range = calculate_square_area(base_position, range_value)
        return [
            hero
            for hero in self.heroes
            if hero.position in positions_list_in_range and hero.player_id != hero.player_id
        ]

    def get_enemies_in_cross_range(self, hero: Hero, range_value: int) -> List[Hero]:
        print(hero.id, range_value)
        base_position = hero.position
        positions_list_in_range = calculate_cross_area(base_position, range_value)
        return [
            hero
            for hero in self.heroes
            if hero.position in positions_list_in_range and hero.player_id != hero.player_id
        ]

    def get_partner_in_square_range(self, hero: Hero, range_value: int) -> List[Hero]:
        base_position = hero.position
        positions_list_in_range = calculate_square_area(base_position, range_value)
        return [
            hero
            for hero in self.heroes
            if hero.position in positions_list_in_range and hero.player_id == hero.player_id
        ]

    def load_buffs(self):
        from primitives.buff.buffs import BuffTemps

        all_buffs = {}
        harm_buffs = {}
        benefit_buffs = {}
        fieldbuffs = {}
        for buff in BuffTemps:
            all_buffs[buff.value.id] = buff.value
            if buff.value.type == BuffTypes.Harm:
                harm_buffs[buff.value.id] = buff.value
            elif buff.value.type == BuffTypes.Benefit:
                benefit_buffs[buff.value.id] = buff.value
        self.all_buffs_temps = all_buffs
        self.harm_buffs_temps = harm_buffs
        self.benefit_buffs_temps = benefit_buffs
        from primitives.fieldbuff.fieldbuffs import FieldBuffsTemps

        for buff in FieldBuffsTemps:
            benefit_buffs[buff.value.id] = buff.value
        self.fieldbuffs_temps = fieldbuffs

    def init_heroes(self, heroes: List[Hero]):
        self.heroes = heroes
        # for hero in self.heroes:
        #     hero.initialize_movable_range(self.battlemap, self.heroes)
        # self.refresh_heroes_attackabled()

    def get_current_player_id(self) -> int:
        return self.get_last_action().player_id

    def get_counter_player_id(self) -> int:
        return 1 - self.get_current_player_id()

    def get_formation_by_player_id(self, player_id: int) -> Formation:
        return [
            formation
            for formation in self.formation
            if formation.player_id == player_id
        ][0] if self.formation else None

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

    def get_hero_list_by_id(self, hero_id: str) -> List[Hero]:
        return [hero for hero in self.heroes if hero.id == hero_id]

    def init_formation(self):
        for hero in self.heroes:
            formation_temp = hero.temp.formation_temp
            if hero.temp.has_formation:
                heroes = self.get_heroes_by_player_id(hero.player_id)
                requirements = (
                    formation_temp.activation_requirements
                )  # [{'profession': Professions.SORCERER}, {'profession': Professions.GUARD}]

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

    def get_field_buff_temp_by_id(self, buff_id: str) -> FieldBuffTemp:
        return self.fieldbuffs_temps[buff_id]

    def get_enemy_by_id(self, hero: Hero, hero_id: str) -> Hero:
        return [
            h for h in self.heroes if h.id == hero_id and h.player_id != hero.player_id
        ][0]

    def init_battlemap(self, map_id: str):
        if not map_id:
            map_id = round(random.random() * 10)
        initial_terrain_map = getattr(Maps, map_id).value
        self.battlemap = BattleMap(11, 11, initial_terrain_map)

    def init_game_heroes(self):
        hero_list = []
        mohuahuangfushen = Hero(
            0,
            HeroeTemps.mohuahuangfushen.value,
            (8, 8),
        )
        mohuahuangfushen.equipments = [Equipments.bingchanchuanzhu_chen.value, Equipments.yurenjinpei.value,
                                       Equipments.xuanqueyaodai.value, Equipments.zanghaijie.value]
        mohuahuangfushen.enabled_passives = ["sanquehuisheng"]
        mohuahuangfushen.enabled_skills = [Skill(0, Skills.anshayouyan.value), Skill(0, Skills.leiyinwanyu.value)]
        mohuahuangfushen.stones = [Stones.get_stone_by_id("wanghuan"), Stones.get_stone_by_id("wanghuan"),
                                   Stones.get_stone_by_id("wanghuan")]
        hero_list.append(mohuahuangfushen)

        fuyayu = Hero(
            0,
            HeroeTemps.fuyayu.value,
            (8, 1),
        )
        fuyayu.equipments = [Equipments.longguxianglian_chen.value, Equipments.pixieyupei_yan.value,
                             Equipments.jiaorenbeige_yan.value, Equipments.youyaoxiuhuan.value]
        fuyayu.enabled_passives = []
        fuyayu.enabled_skills = [Skill(0, Skills.shenqiliuzhuan.value), Skill(0, Skills.zaizhouhaoling.value),
                                 Skill(0, Skills.liwankuanglan.value)]
        fuyayu.stones = [Stones.get_stone_by_id("minkui"), Stones.get_stone_by_id("minkui"),
                         Stones.get_stone_by_id("minkui")]
        hero_list.append(fuyayu)

        huoyong = Hero(
            0,
            HeroeTemps.huoyong.value,
            (8, 0),
        )
        huoyong.equipments = [Equipments.tianhezhusha.value, Equipments.qingshenjingyu.value,
                              Equipments.tianjingfuhun.value, Equipments.zhongyaoyuzhuo.value]
        huoyong.enabled_passives = []
        huoyong.enabled_skills = [Skill(0, Skills.shenqiliuzhuan.value), Skill(0, Skills.zaizhouhaoling.value),
                                  Skill(0, Skills.liwankuanglan.value)]
        huoyong.stones = [Stones.get_stone_by_id("minkui"), Stones.get_stone_by_id("minkui"),
                          Stones.get_stone_by_id("minkui")]
        hero_list.append(huoyong)

        zhenyin = Hero(
            0,
            HeroeTemps.zhenyin.value,
            (9, 1),
        )
        zhenyin.equipments = [Equipments.feiquanmingyu.value, Equipments.lingyuepeihuan_yan.value,
                              Equipments.yanshanpei.value, Equipments.huanniaojie.value]
        zhenyin.enabled_passives = []
        zhenyin.enabled_skills = []
        zhenyin.stones = []
        hero_list.append(zhenyin)

        zhujin = Hero(
            0,
            HeroeTemps.zhujin.value,
            (9, 2),
        )
        zhujin.equipments = [Equipments.tianhezhusha.value, Equipments.yurenjinpei.value,
                             Equipments.xuanqueyaodai.value, Equipments.shuangzhijie.value]
        zhujin.enabled_passives = []
        zhujin.enabled_skills = []
        zhujin.stones = []
        hero_list.append(zhujin)

        mohuahuangfushen = Hero(
            1,
            HeroeTemps.mohuahuangfushen.value,
            (2, 8),
        )
        mohuahuangfushen.equipments = [Equipments.bingchanchuanzhu_chen.value, Equipments.yurenjinpei.value,
                                       Equipments.xuanqueyaodai.value, Equipments.zanghaijie.value]
        mohuahuangfushen.enabled_passives = ["sanquehuisheng"]
        mohuahuangfushen.enabled_skills = [Skill(0, Skills.anshayouyan.value), Skill(0, Skills.leiyinwanyu.value)]
        mohuahuangfushen.stones = [Stones.get_stone_by_id("wanghuan"), Stones.get_stone_by_id("wanghuan"),
                                   Stones.get_stone_by_id("wanghuan")]
        hero_list.append(mohuahuangfushen)

        fuyayu = Hero(
            1,
            HeroeTemps.fuyayu.value,
            (2, 9),
        )
        fuyayu.equipments = [Equipments.longguxianglian_chen.value, Equipments.pixieyupei_yan.value,
                             Equipments.jiaorenbeige_yan.value, Equipments.youyaoxiuhuan.value]
        fuyayu.enabled_passives = []
        fuyayu.enabled_skills = [Skill(0, Skills.shenqiliuzhuan.value), Skill(0, Skills.zaizhouhaoling.value),
                                 Skill(0, Skills.liwankuanglan.value)]
        fuyayu.stones = [Stones.get_stone_by_id("minkui"), Stones.get_stone_by_id("minkui"),
                         Stones.get_stone_by_id("minkui")]
        hero_list.append(fuyayu)

        huoyong = Hero(
            1,
            HeroeTemps.huoyong.value,
            (2, 10),
        )
        huoyong.equipments = [Equipments.tianhezhusha.value, Equipments.qingshenjingyu.value,
                              Equipments.tianjingfuhun.value, Equipments.zhongyaoyuzhuo.value]
        huoyong.enabled_passives = []

        huoyong.enabled_skills = [Skill(0, Skills.shenqiliuzhuan.value), Skill(0, Skills.zaizhouhaoling.value),
                                  Skill(0, Skills.liwankuanglan.value)]
        huoyong.stones = [Stones.get_stone_by_id("minkui"), Stones.get_stone_by_id("minkui"),
                          Stones.get_stone_by_id("minkui")]
        hero_list.append(huoyong)

        zhenyin = Hero(
            1,
            HeroeTemps.zhenyin.value,
            (1, 9),
        )
        zhenyin.equipments = [Equipments.feiquanmingyu.value, Equipments.lingyuepeihuan_yan.value,
                              Equipments.yanshanpei.value, Equipments.huanniaojie.value]
        zhenyin.enabled_passives = []
        zhenyin.enabled_skills = []
        zhenyin.stones = []
        hero_list.append(zhenyin)

        zhujin = Hero(
            1,
            HeroeTemps.zhujin.value,
            (1, 8),
        )
        zhujin.equipments = [Equipments.tianhezhusha.value, Equipments.yurenjinpei.value,
                             Equipments.xuanqueyaodai.value, Equipments.shuangzhijie.value]
        zhujin.enabled_passives = []
        zhujin.enabled_skills = []
        zhujin.stones = []
        hero_list.append(zhujin)

        self.init_heroes(hero_list)

    def init_heroes_position(self):
        for hero in self.heroes:
            self.battlemap.add_hero(hero.position)

    # def refresh_heroes_attackabled(self):
    #     for hero in self.heroes:
    #         hero.initialize_attackable_hero(self.heroes)
