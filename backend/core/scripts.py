from __future__ import annotations

"""内置剧本定义。"""

from backend.core.models import Script
from backend.core.roles import iter_roles


TROUBLE_BREWING_ROLE_IDS = [
    "washerwoman",
    "librarian",
    "investigator",
    "chef",
    "empath",
    "fortune_teller",
    "undertaker",
    "slayer",
    "soldier",
    "monk",
    "ravenkeeper",
    "virgin",
    "mayor",
    "butler",
    "drunk",
    "recluse",
    "saint",
    "poisoner",
    "spy",
    "scarlet_woman",
    "baron",
    "imp",
]

# 按照官方手册整理的不同玩家人数对应的阵营人数配置。
TROUBLE_BREWING_DISTRIBUTION: dict[int, dict[str, int]] = {
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
    id="sample_trouble",
    name="麻烦酝酿示例剧本",
    version="1.0.0",
    roles=iter_roles(TROUBLE_BREWING_ROLE_IDS),
    team_distribution=TROUBLE_BREWING_DISTRIBUTION,
    rules={
        "vote_threshold": "majority",
        "tie_rule": "no_execution_on_tie",
        "storyteller_win_available": False,
    },
)

SCRIPTS = {DEFAULT_SCRIPT.id: DEFAULT_SCRIPT}
