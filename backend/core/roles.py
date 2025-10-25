from __future__ import annotations

"""共享角色定义表。

为避免在多个剧本文件中重复编写角色数据，这里集中维护角色字典。
剧本模块可直接引用 ROLES 中的条目，确保不同剧本能够复用同一份角色配置。
"""

from backend.core.models import ScriptRole

ROLES: dict[str, ScriptRole] = {
    """暗流涌动角色"""
    "洗衣妇": ScriptRole(
        id="洗衣妇",
        name="洗衣妇",
        team="townsfolk",
        tags=["first-night", "info"],
        name_localized={"zh_CN": "洗衣妇"},
        meta={"description": "在第一个夜晚，你会得知两名玩家和一个镇民角色：这两名玩家之一是该角色。"},
    ),
    "图书管理员": ScriptRole(
        id="图书管理员",
        name="图书管理员",
        team="townsfolk",
        tags=["first-night", "info"],
        name_localized={"zh_CN": "图书管理员"},
        meta={
            "description": "在第一个夜晚，你会得知两名玩家和一个外来者角色：这两名玩家之一是该角色。（或者你会得知没有外来者在场）"},
    ),
    "调查员": ScriptRole(
        id="调查员",
        name="调查员",
        team="townsfolk",
        tags=["first-night", "info"],
        name_localized={"zh_CN": "调查员"},
        meta={
            "description": "在第一个夜晚，你会得知两名玩家和一个爪牙角色：这两名玩家之一是该角色。（或者你会得知没有爪牙在场）"},
    ),
    "厨师": ScriptRole(
        id="厨师",
        name="厨师",
        team="townsfolk",
        tags=["first-night", "info"],
        name_localized={"zh_CN": "厨师"},
        meta={"description": "在第一个夜晚，你会得知场上邻座的邪恶玩家有多少对。"},
    ),
    "共情者": ScriptRole(
        id="共情者",
        name="共情者",
        team="townsfolk",
        tags=["nightly", "info"],
        name_localized={"zh_CN": "共情者"},
        meta={"description": "每个夜晚，你会得知你相邻的两位玩家中有多少是邪恶阵营。"},
    ),
    "占卜师": ScriptRole(
        id="占卜师",
        name="占卜师",
        team="townsfolk",
        tags=["nightly", "info"],
        name_localized={"zh_CN": "占卜师"},
        meta={
            "description": "每个夜晚，你要选择两名玩家：你会得知他们之中是否有恶魔。场上会有一名善良玩家始终被你的能力当作恶魔（干扰项）。"},
    ),
    "送葬者": ScriptRole(
        id="送葬者",
        name="送葬者",
        team="townsfolk",
        tags=["nightly", "info"],
        name_localized={"zh_CN": "送葬者"},
        meta={"description": "每个夜晚*，你会得知今天白天被处决玩家的角色。"},
    ),
    "猎人": ScriptRole(
        id="猎人",
        name="猎人",
        team="townsfolk",
        tags=["day", "attack"],
        name_localized={"zh_CN": "猎人"},
        meta={"description": "每局游戏限用一次，你可以在白天公开选择一名玩家：若他是恶魔，该玩家死亡。"},
    ),
    "士兵": ScriptRole(
        id="士兵",
        name="士兵",
        team="townsfolk",
        tags=["passive"],
        name_localized={"zh_CN": "士兵"},
        meta={"description": "恶魔的负面能力对你无效。"},
    ),
    "僧侣": ScriptRole(
        id="僧侣",
        name="僧侣",
        team="townsfolk",
        tags=["nightly", "protect"],
        name_localized={"zh_CN": "僧侣"},
        meta={"description": "每个夜晚*，你要选择一名除你以外的玩家：当晚恶魔的负面能力对其无效。"},
    ),
    "守鸦者": ScriptRole(
        id="守鸦者",
        name="守鸦者",
        team="townsfolk",
        tags=["reaction"],
        name_localized={"zh_CN": "守鸦者"},
        meta={"description": "如果你在夜晚死亡，你会被唤醒，然后你要选择一名玩家：你会得知他的角色。"},
    ),
    "贞洁者": ScriptRole(
        id="贞洁者",
        name="贞洁者",
        team="townsfolk",
        tags=["day", "info"],
        name_localized={"zh_CN": "贞洁者"},
        meta={"description": "当你第一次被提名时，若提名你的玩家是镇民，他立刻被处决。"},
    ),
    "市长": ScriptRole(
        id="市长",
        name="市长",
        team="townsfolk",
        tags=["endgame"],
        name_localized={"zh_CN": "市长"},
        meta={
            "description": "如果只有三名玩家存活且白天没有人被处决，你的阵营获胜。如果你在夜晚即将死亡，可能会有一名其他玩家代替你死亡。"},
    ),
    "管家": ScriptRole(
        id="管家",
        name="管家",
        team="outsider",
        tags=["nightly"],
        name_localized={"zh_CN": "管家"},
        meta={"description": "每个夜晚，你选择一名玩家（除自己以外）：明天白天，只有他能投票时你才能投票。"},
    ),
    "酒鬼": ScriptRole(
        id="酒鬼",
        name="酒鬼",
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
    "陌客": ScriptRole(
        id="陌客",
        name="陌客",
        team="outsider",
        tags=["secret"],
        name_localized={"zh_CN": "陌客"},
        meta={"description": "你可能会被当作邪恶阵营、爪牙或恶魔角色，即使你已死亡。"},
    ),
    "圣徒": ScriptRole(
        id="圣徒",
        name="圣徒",
        team="outsider",
        tags=["day"],
        name_localized={"zh_CN": "圣徒"},
        meta={"description": "如果你死于处决，你的阵营落败。"},
    ),
    "投毒者": ScriptRole(
        id="投毒者",
        name="投毒者",
        team="minion",
        tags=["nightly", "attack"],
        name_localized={"zh_CN": "投毒者"},
        meta={"description": "每个夜晚，你选择一名玩家：他在当晚和明天。"},
    ),
    "间谍": ScriptRole(
        id="间谍",
        name="间谍",
        team="minion",
        tags=["nightly", "info"],
        name_localized={"zh_CN": "间谍"},
        meta={"description": "每个夜晚，你都能查看魔典。你可能会被当作善良阵营、镇民或外来者角色，即使你已死亡。"},
    ),
    "红唇女郎": ScriptRole(
        id="红唇女郎",
        name="红唇女郎",
        team="minion",
        tags=["passive"],
        name_localized={"zh_CN": "红唇女郎"},
        meta={"description": "如果大于等于五名玩家存活时（不包括旅行者）恶魔死亡，你会变成那个恶魔。"},
    ),
    "男爵": ScriptRole(
        id="男爵",
        name="男爵",
        team="minion",
        tags=["setup"],
        name_localized={"zh_CN": "男爵"},
        meta={"description": "会有额外的外来者在场。[+2外来者]"},
    ),
    "小恶魔": ScriptRole(
        id="小恶魔",
        name="小恶魔",
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

    """黯月初升角色"""
    "祖母": ScriptRole(
        id="祖母",
        name="祖母",
        team="townsfolk",
        tags=["first-night", "info"],
        name_localized={"zh_CN": "祖母"},
        meta={"description": "在你的首个夜晚，你会得知一名善良玩家和他的角色。如果恶魔杀死了他，你也会死亡。"},
    ),
    "水手": ScriptRole(
        id="水手",
        name="水手",
        team="townsfolk",
        tags=["nightly", "protect"],
        name_localized={"zh_CN": "水手"},
        meta={"description": "每个夜晚，你要选择一名存活的玩家：你或他之一会醉酒直到下个黄昏。你不会死亡。"},
    ),
    "侍女": ScriptRole(
        id="侍女",
        name="侍女",
        team="townsfolk",
        tags=["nightly", "info"],
        name_localized={"zh_CN": "侍女"},
        meta={"description": "每个夜晚，你选择除自己以外的两名存活玩家：你会得知他们中有几人在当晚因自身能力被唤醒。"},
    ),
    "驱魔人": ScriptRole(
        id="驱魔人",
        name="驱魔人",
        team="townsfolk",
        tags=["nightly", "attack"],
        name_localized={"zh_CN": "驱魔人"},
        meta={
            "description": "每个夜晚*，你选择一名玩家（与上个夜晚不同）：若他是恶魔，他会得知你是驱魔人，但当晚不会被唤醒。"},
    ),
    "旅店老板": ScriptRole(
        id="旅店老板",
        name="旅店老板",
        team="townsfolk",
        tags=["nightly", "protect"],
        name_localized={"zh_CN": "旅店老板"},
        meta={"description": "每个夜晚*，你选择两名玩家：他们当晚不会死亡，但其中一人会醉酒直到下个黄昏。"},
    ),
    "赌徒": ScriptRole(
        id="赌徒",
        name="赌徒",
        team="townsfolk",
        tags=["nightly", "risk"],
        name_localized={"zh_CN": "赌徒"},
        meta={"description": "每个夜晚，你选择一名玩家并猜测其角色：若猜错，你会死亡。"},
    ),
    "造谣者": ScriptRole(
        id="造谣者",
        name="造谣者",
        team="townsfolk",
        tags=["day", "info"],
        name_localized={"zh_CN": "造谣者"},
        meta={"description": "每个白天，你可以公开发表一则声明。若该声明正确，当晚一名玩家会死亡。"},
    ),
    "侍臣": ScriptRole(
        id="侍臣",
        name="侍臣",
        team="townsfolk",
        tags=["limited-use", "nightly"],
        name_localized={"zh_CN": "侍臣"},
        meta={"description": "每局游戏限一次，在夜晚你选择一个角色：若该角色在场，其中一位从当晚起醉酒三天三夜。"},
    ),
    "教授": ScriptRole(
        id="教授",
        name="教授",
        team="townsfolk",
        tags=["limited-use", "nightly", "revive"],
        name_localized={"zh_CN": "教授"},
        meta={"description": "每局游戏限一次，在夜晚时*，你可以选择一名死亡玩家：若他是镇民，他会复活。"},
    ),
    "吟游诗人": ScriptRole(
        id="吟游诗人",
        name="吟游诗人",
        team="townsfolk",
        tags=["reaction"],
        name_localized={"zh_CN": "吟游诗人"},
        meta={"description": "当一名爪牙死于处决时，除你与旅行者外的所有玩家都会醉酒直到明天黄昏。"},
    ),
    "茶艺师": ScriptRole(
        id="茶艺师",
        name="Tea Lady",
        team="townsfolk",
        tags=["passive", "protect"],
        name_localized={"zh_CN": "茶艺师"},
        meta={"description": "若与你邻近的两名存活玩家都是善良阵营，他们不会死亡。"},
    ),
    "和平主义者": ScriptRole(
        id="和平主义者",
        name="Pacifist",
        team="townsfolk",
        tags=["passive", "protect"],
        name_localized={"zh_CN": "和平主义者"},
        meta={"description": "被处决的善良玩家可能不会死亡。"},
    ),
    "弄臣": ScriptRole(
        id="弄臣",
        name="Juggler",
        team="townsfolk",
        tags=["reaction"],
        name_localized={"zh_CN": "弄臣"},
        meta={"description": "当你首次将要死亡时，你不会死亡。"},
    ),
    "修补匠": ScriptRole(
        id="修补匠",
        name="修补匠",
        team="outsider",
        tags=["passive"],
        name_localized={"zh_CN": "修补匠"},
        meta={"description": "你可能随时死亡。"},
    ),
    "月之子": ScriptRole(
        id="月之子",
        name="月之子",
        team="outsider",
        tags=["reaction", "attack"],
        name_localized={"zh_CN": "月之子"},
        meta={"description": "当你得知自己死亡时，你要公开选择一名存活玩家：若他是善良阵营，当晚他会死亡。"},
    ),
    "莽夫": ScriptRole(
        id="莽夫",
        name="莽夫",
        team="outsider",
        tags=["nightly", "convert"],
        name_localized={"zh_CN": "莽夫"},
        meta={"description": "每个夜晚，首个以能力选择你的玩家会醉酒直到下个黄昏。你会转变为他的阵营。"},
    ),
    "疯子": ScriptRole(
        id="疯子",
        name="疯子",
        team="outsider",
        tags=["secret"],
        name_localized={"zh_CN": "疯子"},
        meta={"description": "你以为自己是恶魔，但其实你不是。恶魔知道你是疯子以及你每晚的选择。"},
    ),
    "教父": ScriptRole(
        id="教父",
        name="教父",
        team="minion",
        tags=["first-night", "nightly", "attack"],
        name_localized={"zh_CN": "教父"},
        meta={
            "description": "在你的首个夜晚，你会得知有哪些外来者在场。若外来者在白天死亡，你在当晚选择一名玩家使其死亡。"},
    ),
    "魔鬼代言人": ScriptRole(
        id="魔鬼代言人",
        name="魔鬼代言人",
        team="minion",
        tags=["nightly", "protect"],
        name_localized={"zh_CN": "魔鬼代言人"},
        meta={"description": "每个夜晚，你选择一名存活玩家（与上次不同）：若他明天被处决，他不会死亡。"},
    ),
    "刺客": ScriptRole(
        id="刺客",
        name="刺客",
        team="minion",
        tags=["limited-use", "nightly", "attack"],
        name_localized={"zh_CN": "刺客"},
        meta={"description": "每局游戏限一次，在夜晚时*，你可以选择一名玩家：他会死亡，即使受到任何保护。"},
    ),
    "主谋": ScriptRole(
        id="主谋",
        name="主谋",
        team="minion",
        tags=["reaction", "endgame"],
        name_localized={"zh_CN": "主谋"},
        meta={
            "description": "若恶魔因处决而导致游戏结束，再额外进行一个夜晚和白天。若新的一天善良玩家被处决，则邪恶阵营获胜。"},
    ),
    "僵怖": ScriptRole(
        id="僵怖",
        name="僵怖",
        team="demon",
        tags=["nightly", "attack"],
        name_localized={"zh_CN": "僵怖"},
        meta={
            "description": "每个夜晚*，若今天白天无人死亡，你选择一名玩家使其死亡。你首次死亡后仍被当作死亡但仍存活。",
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
    "普卡": ScriptRole(
        id="普卡",
        name="普卡",
        team="demon",
        tags=["nightly", "poison", "attack"],
        name_localized={"zh_CN": "普卡"},
        meta={
            "description": "每个夜晚，你选择一名玩家使其中毒。上次中毒的玩家会死亡并恢复健康。",
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
    "沙巴洛斯": ScriptRole(
        id="沙巴洛斯",
        name="沙巴洛斯",
        team="demon",
        tags=["nightly", "attack", "revive"],
        name_localized={"zh_CN": "沙巴洛斯"},
        meta={
            "description": "每个夜晚*，你选择两名玩家使其死亡。你上次选择的死亡玩家之一可能会被你复活。",
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
    "珀": ScriptRole(
        id="珀",
        name="珀",
        team="demon",
        tags=["nightly", "attack"],
        name_localized={"zh_CN": "珀"},
        meta={
            "description": "每个夜晚*，你可以选择不杀人。若如此，下一个夜晚你必须杀死三名玩家。",
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


    """夜半狂欢角色"""
    "贵族": ScriptRole(
        id="贵族",
        name="贵族",
        team="townsfolk",
        tags=["first-night", "info"],
        name_localized={"zh_CN": "贵族"},
        meta={"description": "在你的首个夜晚，你会得知三名玩家：其中有且只有一名玩家是邪恶的。"},
    ),
    "舞蛇人": ScriptRole(
        id="舞蛇人",
        name="舞蛇人",
        team="townsfolk",
        tags=["nightly", "convert"],
        name_localized={"zh_CN": "舞蛇人"},
        meta={"description": "每个夜晚，你要选择一名存活的玩家：如果你选中了恶魔，你和他交换角色和阵营，然后他中毒。"},
    ),
    "气球驾驶员": ScriptRole(
        id="气球驾驶员",
        name="气球驾驶员",
        team="townsfolk",
        tags=["nightly", "info"],
        name_localized={"zh_CN": "气球驾驶员"},
        meta={"description": "每个夜晚，你会得知一名不同角色类型的玩家，直到场上所有的角色类型你都得知过一次。（+1 外来者）"},
    ),
    "巡山人": ScriptRole(
        id="巡山人",
        name="巡山人",
        team="townsfolk",
        tags=["limited-use", "nightly", "convert"],
        name_localized={"zh_CN": "巡山人"},
        meta={"description": "每局游戏限一次，在夜晚时，你可以选择一名存活的玩家：如果你选中了落难少女，她会变成一个不在场的镇民角色。（+落难少女）"},
    ),
    "工程师": ScriptRole(
        id="工程师",
        name="工程师",
        team="townsfolk",
        tags=["limited-use", "nightly", "convert"],
        name_localized={"zh_CN": "工程师"},
        meta={"description": "每局游戏限一次，在夜晚时，你可以选择让恶魔变成你选择的恶魔角色，或让所有爪牙变成你选择的爪牙角色。"},
    ),
    "渔夫": ScriptRole(
        id="渔夫",
        name="渔夫",
        team="townsfolk",
        tags=["limited-use", "day", "info"],
        name_localized={"zh_CN": "渔夫"},
        meta={"description": "每局游戏限一次，在白天时，你可以让说书人给你一些能帮助你的阵营获胜的建议。"},
    ),
    "教授": ScriptRole(
        id="教授",
        name="教授",
        team="townsfolk",
        tags=["limited-use", "nightly", "revive"],
        name_localized={"zh_CN": "教授"},
        meta={"description": "每局游戏限一次，在夜晚时*，你可以选择一名死亡的玩家：如果他是镇民，你会将他起死回生（复活）。"},
    ),
    "博学者": ScriptRole(
        id="博学者",
        name="博学者",
        team="townsfolk",
        tags=["day", "info"],
        name_localized={"zh_CN": "博学者"},
        meta={"description": "每个白天，你可以私下询问说书人以得知两条信息：一个是正确的，一个是错误的。"},
    ),
    "农夫": ScriptRole(
        id="农夫",
        name="农夫",
        team="townsfolk",
        tags=["reaction", "convert"],
        name_localized={"zh_CN": "农夫"},
        meta={"description": "如果你在夜晚死亡，一名存活的善良玩家会变成农夫。"},
    ),
    "食人族": ScriptRole(
        id="食人族",
        name="食人族",
        team="townsfolk",
        tags=["reaction", "passive"],
        name_localized={"zh_CN": "食人族"},
        meta={"description": "你拥有上个死于处决的玩家的能力。如果该玩家属于邪恶阵营，你中毒直到下个善良玩家死于处决。"},
    ),
    "罂粟种植者": ScriptRole(
        id="罂粟种植者",
        name="罂粟种植者",
        team="townsfolk",
        tags=["passive", "info"],
        name_localized={"zh_CN": "罂粟种植者"},
        meta={"description": "爪牙和恶魔互相不认识。如果你死亡，当晚他们会互相认识。"},
    ),
    "落难少女": ScriptRole(
        id="落难少女",
        name="落难少女",
        team="outsider",
        tags=["special", "risk"],
        name_localized={"zh_CN": "落难少女"},
        meta={"description": "所有爪牙都知道落难少女在场。每局游戏限一次，任意爪牙可以公开猜测你是落难少女，如果猜对，你的阵营落败。"},
    ),
    "理发师": ScriptRole(
        id="理发师",
        name="理发师",
        team="outsider",
        tags=["reaction", "convert"],
        name_localized={"zh_CN": "理发师"},
        meta={"description": "如果你死亡，在当晚恶魔可以选择两名玩家（不能选择其他恶魔）交换角色。"},
    ),
    "魔像": ScriptRole(
        id="魔像",
        name="魔像",
        team="outsider",
        tags=["day", "attack", "limited-use"],
        name_localized={"zh_CN": "魔像"},
        meta={"description": "每局游戏你只能发起提名一次。当你发起提名时，如果被你提名的玩家不是恶魔，他死亡。"},
    ),
    "灵言师": ScriptRole(
        id="灵言师",
        name="灵言师",
        team="minion",
        tags=["first-night", "conversion"],
        name_localized={"zh_CN": "灵言师"},
        meta={"description": "在你的首个夜晚，你会得知一个关键词。首个说出该关键词的善良玩家会在当晚转变为邪恶阵营。"},
    ),
    "精神病患者": ScriptRole(
        id="精神病患者",
        name="精神病患者",
        team="minion",
        tags=["day", "attack"],
        name_localized={"zh_CN": "精神病患者"},
        meta={"description": "每个白天，在提名开始前，你可以公开选择一名玩家：他死亡。如果你被处决，提名你的玩家需要和你猜拳，只有你输了你才会死亡。"},
    ),
    "麻脸巫婆": ScriptRole(
        id="麻脸巫婆",
        name="麻脸巫婆",
        team="minion",
        tags=["nightly", "convert"],
        name_localized={"zh_CN": "麻脸巫婆"},
        meta={"description": "每个夜晚*，你要选择一名玩家和一个角色，如果该角色不在场，他变成该角色。如果因此创造了一个恶魔，当晚的死亡由说书人决定。"},
    ),
    "哈迪寂亚": ScriptRole(
        id="哈迪寂亚",
        name="哈迪寂亚",
        team="demon",
        tags=["nightly", "attack", "public"],
        name_localized={"zh_CN": "哈迪寂亚"},
        meta={
            "description": "每个夜晚*，你要选择三名玩家（所有玩家都会得知你选了谁）：他们分别秘密决定自己的生死，然后如果他们都存活则都死亡。",
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
    "亡骨魔": ScriptRole(
        id="亡骨魔",
        name="亡骨魔",
        team="demon",
        tags=["nightly", "attack", "poison"],
        name_localized={"zh_CN": "亡骨魔"},
        meta={
            "description": "每个夜晚*，你要选择一名玩家：他死亡。被你杀死的爪牙保留他的能力，且与他邻近的两名镇民之一中毒。[-1 外来者]",
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



    """紫罗兰角色"""
    "艺术家": ScriptRole(
        id="艺术家",
        name="艺术家",
        team="townsfolk",
        tags=["limited-use", "day", "info"],
        name_localized={"zh_CN": "艺术家"},
        meta={"description": "每局游戏限一次，在白天时，你可以私下询问说书人一个是/否答案问题。"},
    ),
    "钟表匠": ScriptRole(
        id="钟表匠",
        name="钟表匠",
        team="townsfolk",
        tags=["first-night", "info"],
        name_localized={"zh_CN": "钟表匠"},
        meta={"description": "在游戏开始时，你会得知恶魔与其最近爪牙之间的距离（1代表相邻）。"},
    ),
    "梦卜者": ScriptRole(
        id="梦卜者",
        name="梦卜者",
        team="townsfolk",
        tags=["nightly", "info"],
        name_localized={"zh_CN": "梦卜者"},
        meta={"description": "每个夜晚，选择一名玩家（不能是自己或旅行者）；你会得知一个善良角色和一个邪恶角色，其中一个是正确的。"},
    ),
    "卖花女": ScriptRole(
        id="卖花女",
        name="卖花女",
        team="townsfolk",
        tags=["nightly", "info"],
        name_localized={"zh_CN": "卖花女"},
        meta={"description": "每个夜晚*，你会得知恶魔是否在白天投过票。"},
    ),
    "杂耍者": ScriptRole(
        id="杂耍者",
        name="杂耍者",
        team="townsfolk",
        tags=["first-day", "info"],
        name_localized={"zh_CN": "杂耍者"},
        meta={"description": "在你的第一个白天，公开猜测至多5名玩家的角色。那个晚上，你能得知猜测正确的个数。"},
    ),
    "数学家": ScriptRole(
        id="数学家",
        name="数学家",
        team="townsfolk",
        tags=["nightly", "info"],
        name_localized={"zh_CN": "数学家"},
        meta={"description": "每个夜晚，你会得知今天白天和这个夜晚总共有多少名玩家的能力因其他角色的能力的影响而未能获得如愿的结果。"},
    ),
    "神谕者": ScriptRole(
        id="神谕者",
        name="神谕者",
        team="townsfolk",
        tags=["nightly", "info"],
        name_localized={"zh_CN": "神谕者"},
        meta={"description": "每个夜晚，你会得知死亡的玩家中有多少名是邪恶阵营的。"},
    ),
    "哲学家": ScriptRole(
        id="哲学家",
        name="哲学家",
        team="townsfolk",
        tags=["limited-use", "nightly", "copy"],
        name_localized={"zh_CN": "哲学家"},
        meta={"description": "每局游戏限一次，在夜晚，挑选一个善良阵营的角色，获得该角色能力。如果该角色在场，则其持续醉酒。"},
    ),
    "贤者": ScriptRole(
        id="贤者",
        name="贤者",
        team="townsfolk",
        tags=["reaction", "info"],
        name_localized={"zh_CN": "贤者"},
        meta={"description": "如果恶魔杀死了你，你会得知两名玩家，其中一位是恶魔。"},
    ),
    "裁缝": ScriptRole(
        id="裁缝",
        name="裁缝",
        team="townsfolk",
        tags=["limited-use", "nightly", "info"],
        name_localized={"zh_CN": "裁缝"},
        meta={"description": "每局游戏限一次，在夜晚时，选择两名玩家（不能是自己）；你会得知他们是否属于同一阵营。"},
    ),
    "公告员": ScriptRole(
        id="公告员",
        name="公告员",
        team="townsfolk",
        tags=["nightly", "info"],
        name_localized={"zh_CN": "公告员"},
        meta={"description": "每个夜晚，你会得知是否有爪牙在今天发起了提名。"},
    ),
    "变种人": ScriptRole(
        id="变种人",
        name="变种人",
        team="outsider",
        tags=["special", "madness"],
        name_localized={"zh_CN": "变种人"},
        meta={"description": "如果你“疯狂”地认为自己是外来者，那么你可能会立即被处决。"},
    ),
    "心上人": ScriptRole(
        id="心上人",
        name="心上人",
        team="outsider",
        tags=["death_trigger", "drunk_effect"],
        name_localized={"zh_CN": "心上人"},
        meta={"description": "当你死亡时，一名其他玩家将持续醉酒。"},
    ),
    "傻瓜": ScriptRole(
        id="傻瓜",
        name="傻瓜",
        team="outsider",
        tags=["death_trigger", "risk"],
        name_localized={"zh_CN": "傻瓜"},
        meta={"description": "当你得知你的死亡时，公开选择一名活着的玩家；如果该玩家是邪恶的，你的阵营落败。"},
    ),
    "镜像双子": ScriptRole(
        id="镜像双子",
        name="镜像双子",
        team="minion",
        tags=["pair", "knowledge", "win_condition"],
        name_localized={"zh_CN": "镜像双子"},
        meta={
            "description": "你和一个对立阵营的玩家相互认识。其中善良阵营的玩家被处决时，邪恶阵营直接获胜。双子都存活时，善良阵营玩家无法获胜。"
        },
    ),
    "洗脑师": ScriptRole(
        id="洗脑师",
        name="洗脑师",
        team="minion",
        tags=["nightly", "madness"],
        name_localized={"zh_CN": "洗脑师"},
        meta={
            "description": "每个夜晚，你选择一名玩家和一个善良阵营角色；该玩家在次日必须“疯狂”地认为自己是该角色，否则可能会被立刻处决。"
        },
    ),
    "巫师": ScriptRole(
        id="巫师",
        name="巫师",
        team="minion",
        tags=["nightly", "nomination_death", "limited"],
        name_localized={"zh_CN": "巫师"},
        meta={
            "description": "每个夜晚，你选择一名玩家；如果该玩家在第二天发起提名，则其死亡。如果仅剩 3 名玩家存活，你失去此能力。"
        },
    ),
    "噬梦游魂": ScriptRole(
        id="噬梦游魂",
        name="噬梦游魂",
        team="demon",
        tags=["night_kill", "outsider_conversion"],
        name_localized={"zh_CN": "噬梦游魂"},
        meta={
            "description": "每个夜晚*，选择并杀死一名玩家。第一个因该能力被杀死的外来者会成为邪恶的噩梦游魂，同时你代替其死亡。",
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
    "腐化邪神": ScriptRole(
        id="腐化邪神",
        name="腐化邪神",
        team="demon",
        tags=["night_kill", "poison"],
        name_localized={"zh_CN": "腐化邪神"},
        meta={
            "description": "每个夜晚*，选择并杀死一名玩家。你两侧最近的村民处于持续中毒状态。",
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
    "迷乱漩涡": ScriptRole(
        id="迷乱漩涡",
        name="迷乱漩涡",
        team="demon",
        tags=["night_kill", "false_info", "alt_win_condition"],
        name_localized={"zh_CN": "迷乱漩涡"},
        meta={
            "description": "每个夜晚*，选择并杀死一名玩家。村民永远会获得错误的信息。每个白天如果没有玩家被处决，邪恶阵营获胜。",
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

    """横行霸道额外角色"""
    "炼金术士": ScriptRole(
        id="炼金术士",
        name="炼金术士",
        team="minion",
        tags=["borrowed_ability"],
        name_localized={"zh_CN": "炼金术士"},
        meta={
            "description": "你拥有一个不在场的爪牙角色的能力。"
        },
    ),
    "将军": ScriptRole(
        id="将军",
        name="将军",
        team="townsfolk",
        tags=["alignment_hint"],
        name_localized={"zh_CN": "将军"},
        meta={
            "description": "每个夜晚，你会得知说书人认为哪个阵营当前更有优势。（善良 / 邪恶 / 均势）"
        },
    ),
    "政客": ScriptRole(
        id="政客",
        name="政客",
        team="townsfolk",
        tags=["alignment_shift", "special_win"],
        name_localized={"zh_CN": "政客"},
        meta={
            "description": "如果你是对你的阵营落败负最大责任的人，你转变阵营并获胜，即使你已死亡。"
        },
    ),
    "异端分子": ScriptRole(
        id="异端分子",
        name="异端分子",
        team="traveller",
        tags=["special_win"],
        name_localized={"zh_CN": "异端分子"},
        meta={
            "description": "对调胜负结果，即使你已死亡。"
        },
    ),
    "恐惧之灵": ScriptRole(
        id="恐惧之灵",
        name="恐惧之灵",
        team="demon",
        tags=["night_action", "curse_link"],
        name_localized={"zh_CN": "恐惧之灵"},
        meta={
            "description": "每个夜晚，你要选择一名玩家；如果你提名的他被处决，他的阵营落败。当你首次选择或更换目标时，所有玩家都会得知你选择了新目标。"
        },
    ),
    "哥布林": ScriptRole(
        id="哥布林",
        name="哥布林",
        team="minion",
        tags=["public_announcement", "execution_win"],
        name_localized={"zh_CN": "哥布林"},
        meta={
            "description": "如果你在被提名后公开声明自己是哥布林且在那个白天被处决，你的阵营获胜。"
        },
    ),
    "痢蛭": ScriptRole(
        id="痢蛭",
        name="痢蛭",
        team="demon",
        tags=["night_action", "poison_link"],
        name_localized={"zh_CN": "痢蛭"},
        meta={
            "description": "每个夜晚*，你选择一名玩家：他死亡。在你的首个夜晚，你要选择一名存活的玩家：他中毒，只有他死亡时你才会一同死亡。",
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
