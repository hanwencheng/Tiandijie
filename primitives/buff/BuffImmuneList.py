from typing import List

immune_dict = {
    # 免疫「移动力降低」
    "xinbu": ["chihuan", "wucui_chihuan", "shuangdong"],
}

# 阻止获得buff
immune_all_benefit_list: List[str] = ["wuhui"]
immune_all_harm_list: List[str] = ["bingqing", "tianjiyin", "wucui_tianjiyin"]
immune_xuanxun_list: List[str] = ["wuyouyu"]

# 免疫buff
prevent_all_benefit_list: List[str] = immune_all_benefit_list + ["duozui"]
prevent_all_harm_list: List[str] = immune_all_harm_list + [""]
