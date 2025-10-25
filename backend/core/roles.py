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
        meta={"description": "在第一个夜晚，你会得知两名玩家和一个镇民角色：这两名玩家之一是该角色。"},
    ),
    "librarian": ScriptRole(
        id="librarian",
        name="Librarian",
        team="townsfolk",
        tags=["first-night", "info"],
        name_localized={"zh_CN": "图书管理员"},
        meta={"description": "在第一个夜晚，你会得知两名玩家和一个外来者角色：这两名玩家之一是该角色。（或者你会得知没有外来者在场）"},
    ),
    "investigator": ScriptRole(
        id="investigator",
        name="Investigator",
        team="townsfolk",
        tags=["first-night", "info"],
        name_localized={"zh_CN": "调查员"},
        meta={"description": "在第一个夜晚，你会得知两名玩家和一个爪牙角色：这两名玩家之一是该角色。（或者你会得知没有爪牙在场）"},
    ),
    "chef": ScriptRole(
        id="chef",
        name="Chef",
        team="townsfolk",
        tags=["first-night", "info"],
        name_localized={"zh_CN": "厨师"},
        meta={"description": "在第一个夜晚，你会得知场上邻座的邪恶玩家有多少对。"},
    ),
    "empath": ScriptRole(
        id="empath",
        name="Empath",
        team="townsfolk",
        tags=["nightly", "info"],
        name_localized={"zh_CN": "共情者"},
        meta={"description": "每个夜晚，你会得知你相邻的两位玩家中有多少是邪恶阵营。"},
    ),
    "fortune_teller": ScriptRole(
        id="fortune_teller",
        name="Fortune Teller",
        team="townsfolk",
        tags=["nightly", "info"],
        name_localized={"zh_CN": "占卜师"},
        meta={"description": "每个夜晚，你要选择两名玩家：你会得知他们之中是否有恶魔。场上会有一名善良玩家始终被你的能力当作恶魔（干扰项）。"},
    ),
    "undertaker": ScriptRole(
        id="undertaker",
        name="Undertaker",
        team="townsfolk",
        tags=["nightly", "info"],
        name_localized={"zh_CN": "送葬者"},
        meta={"description": "每个夜晚*，你会得知今天白天被处决玩家的角色。"},
    ),
    "slayer": ScriptRole(
        id="slayer",
        name="Slayer",
        team="townsfolk",
        tags=["day", "attack"],
        name_localized={"zh_CN": "猎人"},
        meta={"description": "每局游戏限用一次，你可以在白天公开选择一名玩家：若他是恶魔，该玩家死亡。"},
    ),
    "soldier": ScriptRole(
        id="soldier",
        name="Soldier",
        team="townsfolk",
        tags=["passive"],
        name_localized={"zh_CN": "士兵"},
        meta={"description": "恶魔的负面能力对你无效。"},
    ),
    "monk": ScriptRole(
        id="monk",
        name="Monk",
        team="townsfolk",
        tags=["nightly", "protect"],
        name_localized={"zh_CN": "僧侣"},
        meta={"description": "每个夜晚*，你要选择一名除你以外的玩家：当晚恶魔的负面能力对其无效。"},
    ),
    "ravenkeeper": ScriptRole(
        id="ravenkeeper",
        name="Ravenkeeper",
        team="townsfolk",
        tags=["reaction"],
        name_localized={"zh_CN": "守鸦者"},
        meta={"description": "如果你在夜晚死亡，你会被唤醒，然后你要选择一名玩家：你会得知他的角色。"},
    ),
    "virgin": ScriptRole(
        id="virgin",
        name="Virgin",
        team="townsfolk",
        tags=["day", "info"],
        name_localized={"zh_CN": "贞女"},
        meta={"description": "当你第一次被提名时，若提名你的玩家是镇民，他立刻被处决。"},
    ),
    "mayor": ScriptRole(
        id="mayor",
        name="Mayor",
        team="townsfolk",
        tags=["endgame"],
        name_localized={"zh_CN": "市长"},
        meta={"description": "如果只有三名玩家存活且白天没有人被处决，你的阵营获胜。如果你在夜晚即将死亡，可能会有一名其他玩家代替你死亡。"},
    ),
    "butler": ScriptRole(
        id="butler",
        name="Butler",
        team="outsider",
        tags=["nightly"],
        name_localized={"zh_CN": "管家"},
        meta={"description": "每个夜晚，你选择一名玩家（除自己以外）：明天白天，只有他能投票时你才能投票。"},
    ),
    "drunk": ScriptRole(
        id="drunk",
        name="Drunk",
        team="outsider",
        tags=["secret"],
        name_localized={"zh_CN": "酒鬼"},
        meta={
            "description": "你不知道自己是酒鬼。你认为自己是某个镇民角色，但其实你不是。",
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
        name_localized={"zh_CN": "陌客"},
        meta={"description": "你可能会被当作邪恶阵营、爪牙或恶魔角色，即使你已死亡。"},
    ),
    "saint": ScriptRole(
        id="saint",
        name="Saint",
        team="outsider",
        tags=["day"],
        name_localized={"zh_CN": "圣徒"},
        meta={"description": "如果你死于处决，你的阵营落败。"},
    ),
    "poisoner": ScriptRole(
        id="poisoner",
        name="Poisoner",
        team="minion",
        tags=["nightly", "attack"],
        name_localized={"zh_CN": "投毒者"},
        meta={"description": "每个夜晚，你选择一名玩家：他在当晚和明天。"},
    ),
    "spy": ScriptRole(
        id="spy",
        name="Spy",
        team="minion",
        tags=["nightly", "info"],
        name_localized={"zh_CN": "间谍"},
        meta={"description": "每个夜晚，你都能查看魔典。你可能会被当作善良阵营、镇民或外来者角色，即使你已死亡。"},
    ),
    "scarlet_woman": ScriptRole(
        id="scarlet_woman",
        name="Scarlet Woman",
        team="minion",
        tags=["passive"],
        name_localized={"zh_CN": "绯红女子"},
        meta={"description": "如果大于等于五名玩家存活时（不包括旅行者）恶魔死亡，你会变成那个恶魔。"},
    ),
    "baron": ScriptRole(
        id="baron",
        name="Baron",
        team="minion",
        tags=["setup"],
        name_localized={"zh_CN": "男爵"},
        meta={"description": "会有额外的外来者在场。[+2外来者]"},
    ),
    "imp": ScriptRole(
        id="imp",
        name="Imp",
        team="demon",
        tags=["nightly", "attack"],
        name_localized={"zh_CN": "小恶魔"},
        meta={
            "description": "每个夜晚*，你要选择一名玩家：他死亡。如果你以这种方式自杀，一名爪牙会变成小恶魔。",
            "attachment_slots": [
                {
                    "id": "demon_bluff",
                    "label": "恶魔伪装角色",
                    "count": 3,
                    "team_filter": ["townsfolk", "outsider"],
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
