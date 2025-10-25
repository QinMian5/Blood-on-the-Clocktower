from __future__ import annotations

"""共享角色定义表。

为避免在多个剧本文件中重复编写角色数据，这里集中维护角色字典。
剧本模块可直接引用 ROLES 中的条目，确保不同剧本能够复用同一份角色配置。
"""

from backend.core.models import ScriptRole


ROLES: dict[str, ScriptRole] = {
    "washerwoman": ScriptRole(
        id="washerwoman",
        name="Washerwoman",
        team="townsfolk",
        tags=["first-night", "info"],
        name_localized={"zh_CN": "洗衣妇"},
        meta={"description": "第一夜得知两名玩家之一是特定镇民。"},
    ),
    "librarian": ScriptRole(
        id="librarian",
        name="Librarian",
        team="townsfolk",
        tags=["first-night", "info"],
        name_localized={"zh_CN": "图书管理员"},
        meta={"description": "第一夜得知两名玩家之一是外来者；若无外来者则得知一名玩家不是外来者。"},
    ),
    "investigator": ScriptRole(
        id="investigator",
        name="Investigator",
        team="townsfolk",
        tags=["first-night", "info"],
        name_localized={"zh_CN": "调查员"},
        meta={"description": "第一夜得知两名玩家之一是爪牙。"},
    ),
    "chef": ScriptRole(
        id="chef",
        name="Chef",
        team="townsfolk",
        tags=["first-night", "info"],
        name_localized={"zh_CN": "厨师"},
        meta={"description": "第一夜得知有多少对相邻的玩家同时是爪牙与恶魔。"},
    ),
    "empath": ScriptRole(
        id="empath",
        name="Empath",
        team="townsfolk",
        tags=["nightly", "info"],
        name_localized={"zh_CN": "共情者"},
        meta={"description": "每个夜晚得知与你相邻的存活玩家中有多少恶魔。"},
    ),
    "fortune_teller": ScriptRole(
        id="fortune_teller",
        name="Fortune Teller",
        team="townsfolk",
        tags=["nightly", "info"],
        name_localized={"zh_CN": "算命师"},
        meta={"description": "每个夜晚选择两名玩家，若其中有人是恶魔你会得到提示（红衣女子可能造成误导）。"},
    ),
    "undertaker": ScriptRole(
        id="undertaker",
        name="Undertaker",
        team="townsfolk",
        tags=["nightly", "info"],
        name_localized={"zh_CN": "殡葬师"},
        meta={"description": "每个夜晚得知当天被处决玩家的真实角色。"},
    ),
    "slayer": ScriptRole(
        id="slayer",
        name="Slayer",
        team="townsfolk",
        tags=["day", "attack"],
        name_localized={"zh_CN": "猎魔人"},
        meta={"description": "每局一次在白天公开指向一名玩家，若其是恶魔则立即死亡。"},
    ),
    "soldier": ScriptRole(
        id="soldier",
        name="Soldier",
        team="townsfolk",
        tags=["passive"],
        name_localized={"zh_CN": "士兵"},
        meta={"description": "你不会死于恶魔的夜间攻击。"},
    ),
    "monk": ScriptRole(
        id="monk",
        name="Monk",
        team="townsfolk",
        tags=["nightly", "protect"],
        name_localized={"zh_CN": "僧侣"},
        meta={"description": "每个夜晚保护一名其他玩家免受恶魔攻击。"},
    ),
    "ravenkeeper": ScriptRole(
        id="ravenkeeper",
        name="Ravenkeeper",
        team="townsfolk",
        tags=["reaction"],
        name_localized={"zh_CN": "乌鸦守护者"},
        meta={"description": "当你在夜晚死亡时，你可以立刻得知任意一名玩家的角色。"},
    ),
    "virgin": ScriptRole(
        id="virgin",
        name="Virgin",
        team="townsfolk",
        tags=["day", "info"],
        name_localized={"zh_CN": "贞女"},
        meta={"description": "第一次被提名时，若提名者是镇民则其立即被处决且你幸存；否则你失去能力。"},
    ),
    "mayor": ScriptRole(
        id="mayor",
        name="Mayor",
        team="townsfolk",
        tags=["endgame"],
        name_localized={"zh_CN": "市长"},
        meta={"description": "若处决投票平票则无人处决；你可能在夜晚死亡时改由其他玩家代替。"},
    ),
    "butler": ScriptRole(
        id="butler",
        name="Butler",
        team="outsider",
        tags=["nightly"],
        name_localized={"zh_CN": "管家"},
        meta={"description": "你必须跟随指定的镇民投票；你认为自己只能在其投票时参与。"},
    ),
    "drunk": ScriptRole(
        id="drunk",
        name="Drunk",
        team="outsider",
        tags=["secret"],
        name_localized={"zh_CN": "酒鬼"},
        meta={
            "description": "你以为自己是某个镇民，但其实是酒鬼且能力无效。",
            "attachment_slots": [
                {
                    "id": "drunk_false_role",
                    "label": "酒鬼误以为的角色",
                    "count": 1,
                    "team_filter": ["townsfolk"],
                    "allow_duplicates": False,
                    "owner_view": "replace_primary",
                }
            ],
        },
    ),
    "recluse": ScriptRole(
        id="recluse",
        name="Recluse",
        team="outsider",
        tags=["secret"],
        name_localized={"zh_CN": "隐士"},
        meta={"description": "你可能被主持人视为爪牙或恶魔。"},
    ),
    "saint": ScriptRole(
        id="saint",
        name="Saint",
        team="outsider",
        tags=["day"],
        name_localized={"zh_CN": "圣徒"},
        meta={"description": "如果你在白天被处决，善阵营立即失败。"},
    ),
    "poisoner": ScriptRole(
        id="poisoner",
        name="Poisoner",
        team="minion",
        tags=["nightly", "attack"],
        name_localized={"zh_CN": "投毒者"},
        meta={"description": "每个夜晚使一名玩家中毒，他们的能力会产生错误结果。"},
    ),
    "spy": ScriptRole(
        id="spy",
        name="Spy",
        team="minion",
        tags=["nightly", "info"],
        name_localized={"zh_CN": "间谍"},
        meta={"description": "你能看到主持人的所有手册信息，并被当作善方角色。"},
    ),
    "scarlet_woman": ScriptRole(
        id="scarlet_woman",
        name="Scarlet Woman",
        team="minion",
        tags=["passive"],
        name_localized={"zh_CN": "绯红女子"},
        meta={"description": "若恶魔在至少3名存活玩家时死亡，你可以立即接替成为恶魔。"},
    ),
    "baron": ScriptRole(
        id="baron",
        name="Baron",
        team="minion",
        tags=["setup"],
        name_localized={"zh_CN": "男爵"},
        meta={"description": "游戏中额外增加两名外来者，同时减少两名镇民。"},
    ),
    "imp": ScriptRole(
        id="imp",
        name="Imp",
        team="demon",
        tags=["nightly", "attack"],
        name_localized={"zh_CN": "小恶魔"},
        meta={
            "description": "每个夜晚杀死一名玩家；你可以自杀并让一名爪牙成为新的恶魔。",
            "attachment_slots": [
                {
                    "id": "demon_bluff",
                    "label": "恶魔伪装角色",
                    "count": 3,
                    "team_filter": ["townsfolk", "outsider", "minion"],
                    "allow_duplicates": False,
                }
            ],
        },
    ),
}


def get_role(role_id: str) -> ScriptRole:
    """根据角色 ID 获取配置，不存在时抛出友好异常。"""

    try:
        return ROLES[role_id]
    except KeyError as exc:  # pragma: no cover - 防御性分支
        raise ValueError(f"未知角色 ID: {role_id}") from exc


def iter_roles(role_ids: list[str]) -> list[ScriptRole]:
    """按照提供的 ID 列表返回对应的角色对象。"""

    return [get_role(role_id) for role_id in role_ids]


ALL_ROLES: list[ScriptRole] = list(ROLES.values())
