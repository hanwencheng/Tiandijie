from typing import List

from helpers import is_normal_attack_magic
from primitives.hero.Element import Elements
from primitives.hero.HeroBasics import Gender, Professions
from primitives.hero.Attributes import Attributes, generate_max_level_attributes
from primitives.hero.BasicAttributes import AttributesTuple
from primitives.skill.SkillTemp import create_normal_attack_skill
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from primitives import Passive


class HeroTemp:
    def __init__(
        self,
        basicInfo,
        element,
        profession,
        level0_attributes,
        growth_coefficients,
        skills,
    ):
        self.current_life: float = 1
        self.name = "玄羽"
        self.rarity = "绝"
        self.id = "xuanyu"
        self.is_normal_attack_magic = is_normal_attack_magic(profession)
        self.normal_attack = create_normal_attack_skill(element, profession, None)
        self.flyable = False
        self.has_formation = False
        self.formation_temp = None
        self.passives: List[Passive] = []
        self.gender = Gender.FEMALE
        if self.gender not in Gender:
            raise ValueError("性别必须是‘男’或‘女’")
        self.element: Elements = Elements.DARK
        self.profession: Professions = profession
        self.movement: int = 3
        self.level0_attributes: Attributes = Attributes(172, 89, 31, 22, 23, 60)
        self.growth_coefficients: AttributesTuple = growth_coefficients
        self.talent = "玄翎鸩影"
        self.initial_skill = "逐风破"
        self.skills = {
            "初级": ["魔", "幽镝戒杀"],
            "中级": ["飞羽憾魄"],
            "高级": ["迅", "奋力", "漫天箭雨", "摧心闇矢"],
            "特级": ["晦弓在弦"],
            "极级": ["魂", "贯甲咒"],
        }
        self.weapons = ["柳木弓", "缠银弓", "暮云弓", "幽蚕弓"]
        self.weapon_features = ["鹤唳", "翎牙", "锁心"]
        # Attributes initialization
        self.current_attributes: Attributes = None
        self.initialize_attributes()

    def initialize_attributes(self):
        generate_max_level_attributes(
            self.current_attributes, self.growth_coefficients, self.profession
        )
        self.current_life = self.current_attributes.life

