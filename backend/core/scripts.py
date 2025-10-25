from __future__ import annotations

"""内置剧本定义。"""

from backend.core.models import Script
from backend.core.roles import iter_roles

# 按照官方手册整理的不同玩家人数对应的阵营人数配置。
DISTRIBUTION: dict[int, dict[str, int]] = {
    5: {"townsfolk": 3, "outsider": 0, "minion": 1, "demon": 1},
    6: {"townsfolk": 3, "outsider": 1, "minion": 1, "demon": 1},
    7: {"townsfolk": 5, "outsider": 0, "minion": 1, "demon": 1},
    8: {"townsfolk": 5, "outsider": 1, "minion": 1, "demon": 1},
    9: {"townsfolk": 5, "outsider": 2, "minion": 1, "demon": 1},
    10: {"townsfolk": 7, "outsider": 0, "minion": 2, "demon": 1},
    11: {"townsfolk": 7, "outsider": 1, "minion": 2, "demon": 1},
    12: {"townsfolk": 7, "outsider": 2, "minion": 2, "demon": 1},
    13: {"townsfolk": 9, "outsider": 0, "minion": 3, "demon": 1},
    14: {"townsfolk": 9, "outsider": 1, "minion": 3, "demon": 1},
    15: {"townsfolk": 9, "outsider": 2, "minion": 3, "demon": 1},
}


DEFAULT_SCRIPT = Script(
    id="暗流涌动",
    name="暗流涌动",
    version="1.0.0",
    roles=iter_roles(["洗衣妇", "图书管理员", "调查员", "厨师", "共情者", "占卜师", "送葬者", "僧侣", 
                      "守鸦人", "贞洁者", "猎手", "士兵", "镇长", "管家", "陌客", "酒鬼", "圣徒",
                      "投毒者", "男爵", "间谍", "红唇女郎", "小恶魔"]),
    team_distribution=DISTRIBUTION,
    rules={
        "vote_threshold": "majority",
        "tie_rule": "no_execution_on_tie",
        "storyteller_win_available": False,
    },
)

SCRIPTS = {
    "暗流涌动": Script(
    id="暗流涌动",
    name="暗流涌动",
    version="1.0.0",
    roles=iter_roles(["洗衣妇", "图书管理员", "调查员", "厨师", "共情者", "占卜师", "送葬者", "僧侣", 
                      "守鸦人", "贞洁者", "猎手", "士兵", "镇长", "管家", "陌客", "酒鬼", "圣徒",
                      "投毒者", "男爵", "间谍", "红唇女郎", "小恶魔"]),
    team_distribution=DISTRIBUTION,
    rules={
        "vote_threshold": "majority",
        "tie_rule": "no_execution_on_tie",
        "storyteller_win_available": False,
    }), 
    
    "黯月初升": Script(
    id="黯月初升",
    name="黯月初升",
    version="1.0.0",
    roles=iter_roles(['祖母', '水手', '侍女', '驱魔人', '旅店老板', '赌徒', '造谣者', '侍臣', '教授', 
                      '吟游诗人', '茶艺师', '和平主义者', '弄臣', '莽夫', '修补匠', '疯子', '月之子',
                      '教父', '刺客', '魔鬼代言人', '主谋', '僵怖', '沙巴洛斯', '普卡', '珀']),
    team_distribution=DISTRIBUTION,
    rules={
        "vote_threshold": "majority",
        "tie_rule": "no_execution_on_tie",
        "storyteller_win_available": False,
    }), 

    "夜半狂欢": Script(
    id="夜半狂欢",
    name="夜半狂欢",
    version="1.0.0",
    roles=iter_roles(['贵族', '舞蛇人', '气球驾驶员', '巡山人', '工程师', '渔夫', '教授', '博学者', 
                      '失忆者', '农夫', '食人族', '罂粟种植者', '酒鬼', '落难少女', '理发师', '魔像',
                      '投毒者', '灵言师', '精神病患者', '麻脸巫婆', '哈迪寂亚', '亡骨魔']),
    team_distribution=DISTRIBUTION,
    rules={
        "vote_threshold": "majority",
        "tie_rule": "no_execution_on_tie",
        "storyteller_win_available": False,
    }), 

    "紫罗兰教派": Script(
    id="紫罗兰教派",
    name="紫罗兰教派",
    version="1.0.0",
    roles=iter_roles(["艺术家", "钟表匠", "梦卜者", "卖花女", "杂耍者", "数学家", "神谕者", "哲学家", 
                      "贤者", "博学者", "裁缝", "舞蛇人", "公告员", "变种人", "理发师", "心上人",
                      "傻瓜", "镜像双子", "洗脑师", "巫师", "麻脸巫婆", "噬梦游魂", "腐化邪神", "亡骨魔",
                      "迷乱漩涡"]),
    team_distribution=DISTRIBUTION,
    rules={
        "vote_threshold": "majority",
        "tie_rule": "no_execution_on_tie",
        "storyteller_win_available": False,
    }),

    "横行霸道": Script(
    id="横行霸道",
    name="横行霸道",
    version="1.0.0",
    roles=iter_roles(["炼金术士", "水手", "将军", "占卜师", "舞蛇人", "博学者", "哲学家", "杂耍者",
                      "渔夫", "巡山人", "茶艺师", "食人族", "罂粟种植者", "落难少女", "疯子", "政客",
                      "异端分子", "理发师", "投毒者", "魔鬼代言人", "恐惧之灵", "精神病患者", "哥布林", 
                      "痢蛭", "小恶魔"]),
    team_distribution=DISTRIBUTION,
    rules={
        "vote_threshold": "majority",
        "tie_rule": "no_execution_on_tie",
        "storyteller_win_available": False,
    }),
          }
