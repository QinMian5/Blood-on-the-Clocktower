from __future__ import annotations

"""共享角色定义表。

为避免在多个剧本文件中重复编写角色数据，这里集中维护角色字典。
剧本模块可直接引用 ROLES 中的条目，确保不同剧本能够复用同一份角色配置。
"""

from backend.core.models import ScriptRole

ROLES: dict[str, ScriptRole] = {
    """暗流涌动角色"""
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
        meta={
            "description": "在第一个夜晚，你会得知两名玩家和一个外来者角色：这两名玩家之一是该角色。（或者你会得知没有外来者在场）"},
    ),
    "investigator": ScriptRole(
        id="investigator",
        name="Investigator",
        team="townsfolk",
        tags=["first-night", "info"],
        name_localized={"zh_CN": "调查员"},
        meta={
            "description": "在第一个夜晚，你会得知两名玩家和一个爪牙角色：这两名玩家之一是该角色。（或者你会得知没有爪牙在场）"},
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
        meta={
            "description": "每个夜晚，你要选择两名玩家：你会得知他们之中是否有恶魔。场上会有一名善良玩家始终被你的能力当作恶魔（干扰项）。"},
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
        meta={
            "description": "如果只有三名玩家存活且白天没有人被处决，你的阵营获胜。如果你在夜晚即将死亡，可能会有一名其他玩家代替你死亡。"},
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

    """黯月初升角色"""
    "grandmother": ScriptRole(
        id="grandmother",
        name="Grandmother",
        team="townsfolk",
        tags=["first-night", "info"],
        name_localized={"zh_CN": "祖母"},
        meta={"description": "在你的首个夜晚，你会得知一名善良玩家和他的角色。如果恶魔杀死了他，你也会死亡。"},
    ),
    "sailor": ScriptRole(
        id="sailor",
        name="Sailor",
        team="townsfolk",
        tags=["nightly", "protect"],
        name_localized={"zh_CN": "水手"},
        meta={"description": "每个夜晚，你要选择一名存活的玩家：你或他之一会醉酒直到下个黄昏。你不会死亡。"},
    ),
    "chambermaid": ScriptRole(
        id="chambermaid",
        name="Chambermaid",
        team="townsfolk",
        tags=["nightly", "info"],
        name_localized={"zh_CN": "侍女"},
        meta={"description": "每个夜晚，你选择除自己以外的两名存活玩家：你会得知他们中有几人在当晚因自身能力被唤醒。"},
    ),
    "exorcist": ScriptRole(
        id="exorcist",
        name="Exorcist",
        team="townsfolk",
        tags=["nightly", "attack"],
        name_localized={"zh_CN": "驱魔人"},
        meta={
            "description": "每个夜晚*，你选择一名玩家（与上个夜晚不同）：若他是恶魔，他会得知你是驱魔人，但当晚不会被唤醒。"},
    ),
    "innkeeper": ScriptRole(
        id="innkeeper",
        name="Innkeeper",
        team="townsfolk",
        tags=["nightly", "protect"],
        name_localized={"zh_CN": "旅店老板"},
        meta={"description": "每个夜晚*，你选择两名玩家：他们当晚不会死亡，但其中一人会醉酒直到下个黄昏。"},
    ),
    "gambler": ScriptRole(
        id="gambler",
        name="Gambler",
        team="townsfolk",
        tags=["nightly", "risk"],
        name_localized={"zh_CN": "赌徒"},
        meta={"description": "每个夜晚，你选择一名玩家并猜测其角色：若猜错，你会死亡。"},
    ),
    "gossip": ScriptRole(
        id="gossip",
        name="Gossip",
        team="townsfolk",
        tags=["day", "info"],
        name_localized={"zh_CN": "造谣者"},
        meta={"description": "每个白天，你可以公开发表一则声明。若该声明正确，当晚一名玩家会死亡。"},
    ),
    "courtier": ScriptRole(
        id="courtier",
        name="Courtier",
        team="townsfolk",
        tags=["limited-use", "nightly"],
        name_localized={"zh_CN": "侍臣"},
        meta={"description": "每局游戏限一次，在夜晚你选择一个角色：若该角色在场，其中一位从当晚起醉酒三天三夜。"},
    ),
    "professor": ScriptRole(
        id="professor",
        name="Professor",
        team="townsfolk",
        tags=["limited-use", "nightly", "revive"],
        name_localized={"zh_CN": "教授"},
        meta={"description": "每局游戏限一次，在夜晚时*，你可以选择一名死亡玩家：若他是镇民，他会复活。"},
    ),
    "minstrel": ScriptRole(
        id="minstrel",
        name="Minstrel",
        team="townsfolk",
        tags=["reaction"],
        name_localized={"zh_CN": "吟游诗人"},
        meta={"description": "当一名爪牙死于处决时，除你与旅行者外的所有玩家都会醉酒直到明天黄昏。"},
    ),
    "tea_lady": ScriptRole(
        id="tea_lady",
        name="Tea Lady",
        team="townsfolk",
        tags=["passive", "protect"],
        name_localized={"zh_CN": "茶艺师"},
        meta={"description": "若与你邻近的两名存活玩家都是善良阵营，他们不会死亡。"},
    ),
    "pacifist": ScriptRole(
        id="pacifist",
        name="Pacifist",
        team="townsfolk",
        tags=["passive", "protect"],
        name_localized={"zh_CN": "和平主义者"},
        meta={"description": "被处决的善良玩家可能不会死亡。"},
    ),
    "jinx": ScriptRole(
        id="jinx",
        name="Juggler",
        team="townsfolk",
        tags=["reaction"],
        name_localized={"zh_CN": "弄臣"},
        meta={"description": "当你首次将要死亡时，你不会死亡。"},
    ),
    "tinker": ScriptRole(
        id="tinker",
        name="Tinker",
        team="outsider",
        tags=["passive"],
        name_localized={"zh_CN": "修补匠"},
        meta={"description": "你可能随时死亡。"},
    ),
    "moonchild": ScriptRole(
        id="moonchild",
        name="Moonchild",
        team="outsider",
        tags=["reaction", "attack"],
        name_localized={"zh_CN": "月之子"},
        meta={"description": "当你得知自己死亡时，你要公开选择一名存活玩家：若他是善良阵营，当晚他会死亡。"},
    ),
    "golem": ScriptRole(
        id="goon",
        name="Goon",
        team="outsider",
        tags=["nightly", "convert"],
        name_localized={"zh_CN": "莽夫"},
        meta={"description": "每个夜晚，首个以能力选择你的玩家会醉酒直到下个黄昏。你会转变为他的阵营。"},
    ),
    "lunatic": ScriptRole(
        id="lunatic",
        name="Lunatic",
        team="outsider",
        tags=["secret"],
        name_localized={"zh_CN": "疯子"},
        meta={"description": "你以为自己是恶魔，但其实你不是。恶魔知道你是疯子以及你每晚的选择。"},
    ),
    "godfather": ScriptRole(
        id="godfather",
        name="Godfather",
        team="minion",
        tags=["first-night", "nightly", "attack"],
        name_localized={"zh_CN": "教父"},
        meta={
            "description": "在你的首个夜晚，你会得知有哪些外来者在场。若外来者在白天死亡，你在当晚选择一名玩家使其死亡。"},
    ),
    "devils_advocate": ScriptRole(
        id="devils_advocate",
        name="Devil’s Advocate",
        team="minion",
        tags=["nightly", "protect"],
        name_localized={"zh_CN": "魔鬼代言人"},
        meta={"description": "每个夜晚，你选择一名存活玩家（与上次不同）：若他明天被处决，他不会死亡。"},
    ),
    "assassin": ScriptRole(
        id="assassin",
        name="Assassin",
        team="minion",
        tags=["limited-use", "nightly", "attack"],
        name_localized={"zh_CN": "刺客"},
        meta={"description": "每局游戏限一次，在夜晚时*，你可以选择一名玩家：他会死亡，即使受到任何保护。"},
    ),
    "mastermind": ScriptRole(
        id="mastermind",
        name="Mastermind",
        team="minion",
        tags=["reaction", "endgame"],
        name_localized={"zh_CN": "主谋"},
        meta={
            "description": "若恶魔因处决而导致游戏结束，再额外进行一个夜晚和白天。若新的一天善良玩家被处决，则邪恶阵营获胜。"},
    ),
    "zombuul": ScriptRole(
        id="zombuul",
        name="Zombuul",
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
    "pukka": ScriptRole(
        id="pukka",
        name="Pukka",
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
    "shabaloth": ScriptRole(
        id="shabaloth",
        name="Shabaloth",
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
    "po": ScriptRole(
        id="po",
        name="Po",
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
    "aristocrat": ScriptRole(
        id="aristocrat",
        name="Aristocrat",
        team="townsfolk",
        tags=["first-night", "info"],
        name_localized={"zh_CN": "贵族"},
        meta={"description": "在你的首个夜晚，你会得知三名玩家：其中有且只有一名玩家是邪恶的。"},
    ),
    "snake_charmer": ScriptRole(
        id="snake_charmer",
        name="Snake Charmer",
        team="townsfolk",
        tags=["nightly", "convert"],
        name_localized={"zh_CN": "舞蛇人"},
        meta={"description": "每个夜晚，你要选择一名存活的玩家：如果你选中了恶魔，你和他交换角色和阵营，然后他中毒。"},
    ),
    "balloonist": ScriptRole(
        id="balloonist",
        name="Balloonist",
        team="townsfolk",
        tags=["nightly", "info"],
        name_localized={"zh_CN": "气球驾驶员"},
        meta={"description": "每个夜晚，你会得知一名不同角色类型的玩家，直到场上所有的角色类型你都得知过一次。（+1 外来者）"},
    ),
    "hiker": ScriptRole(
        id="hiker",
        name="Hiker",
        team="townsfolk",
        tags=["limited-use", "nightly", "convert"],
        name_localized={"zh_CN": "巡山人"},
        meta={"description": "每局游戏限一次，在夜晚时，你可以选择一名存活的玩家：如果你选中了落难少女，她会变成一个不在场的镇民角色。（+落难少女）"},
    ),
    "engineer": ScriptRole(
        id="engineer",
        name="Engineer",
        team="townsfolk",
        tags=["limited-use", "nightly", "convert"],
        name_localized={"zh_CN": "工程师"},
        meta={"description": "每局游戏限一次，在夜晚时，你可以选择让恶魔变成你选择的恶魔角色，或让所有爪牙变成你选择的爪牙角色。"},
    ),
    "fisherman": ScriptRole(
        id="fisherman",
        name="Fisherman",
        team="townsfolk",
        tags=["limited-use", "day", "info"],
        name_localized={"zh_CN": "渔夫"},
        meta={"description": "每局游戏限一次，在白天时，你可以让说书人给你一些能帮助你的阵营获胜的建议。"},
    ),
    "professor": ScriptRole(
        id="professor",
        name="Professor",
        team="townsfolk",
        tags=["limited-use", "nightly", "revive"],
        name_localized={"zh_CN": "教授"},
        meta={"description": "每局游戏限一次，在夜晚时*，你可以选择一名死亡的玩家：如果他是镇民，你会将他起死回生（复活）。"},
    ),
    "savant": ScriptRole(
        id="savant",
        name="Savant",
        team="townsfolk",
        tags=["day", "info"],
        name_localized={"zh_CN": "博学者"},
        meta={"description": "每个白天，你可以私下询问说书人以得知两条信息：一个是正确的，一个是错误的。"},
    ),
    "farmer": ScriptRole(
        id="farmer",
        name="Farmer",
        team="townsfolk",
        tags=["reaction", "convert"],
        name_localized={"zh_CN": "农夫"},
        meta={"description": "如果你在夜晚死亡，一名存活的善良玩家会变成农夫。"},
    ),
    "cannibal": ScriptRole(
        id="cannibal",
        name="Cannibal",
        team="townsfolk",
        tags=["reaction", "passive"],
        name_localized={"zh_CN": "食人族"},
        meta={"description": "你拥有上个死于处决的玩家的能力。如果该玩家属于邪恶阵营，你中毒直到下个善良玩家死于处决。"},
    ),
    "orchardist": ScriptRole(
        id="orchardist",
        name="Orchardist",
        team="townsfolk",
        tags=["passive", "info"],
        name_localized={"zh_CN": "释粟种植者"},
        meta={"description": "爪牙和恶魔互相不认识。如果你死亡，当晚他们会互相认识。"},
    ),
    "damsel": ScriptRole(
        id="damsel",
        name="Damsel",
        team="outsider",
        tags=["special", "risk"],
        name_localized={"zh_CN": "落难少女"},
        meta={"description": "所有爪牙都知道落难少女在场。每局游戏限一次，任意爪牙可以公开猜测你是落难少女，如果猜对，你的阵营落败。"},
    ),
    "barber": ScriptRole(
        id="barber",
        name="Barber",
        team="outsider",
        tags=["reaction", "convert"],
        name_localized={"zh_CN": "理发师"},
        meta={"description": "如果你死亡，在当晚恶魔可以选择两名玩家（不能选择其他恶魔）交换角色。"},
    ),
    "sculptor": ScriptRole(
        id="sculptor",
        name="Sculptor",
        team="outsider",
        tags=["day", "attack", "limited-use"],
        name_localized={"zh_CN": "魔像"},
        meta={"description": "每局游戏你只能发起提名一次。当你发起提名时，如果被你提名的玩家不是恶魔，他死亡。"},
    ),
    "cerenovus": ScriptRole(
        id="cerenovus",
        name="Cerenovus",
        team="minion",
        tags=["first-night", "conversion"],
        name_localized={"zh_CN": "灵言师"},
        meta={"description": "在你的首个夜晚，你会得知一个关键词。首个说出该关键词的善良玩家会在当晚转变为邪恶阵营。"},
    ),
    "lunatic_patient": ScriptRole(
        id="lunatic_patient",
        name="Lunatic Patient",
        team="minion",
        tags=["day", "attack"],
        name_localized={"zh_CN": "精神病患者"},
        meta={"description": "每个白天，在提名开始前，你可以公开选择一名玩家：他死亡。如果你被处决，提名你的玩家需要和你猜拳，只有你输了你才会死亡。"},
    ),
    "witch": ScriptRole(
        id="witch",
        name="Witch",
        team="minion",
        tags=["nightly", "convert"],
        name_localized={"zh_CN": "麻脸巫婆"},
        meta={"description": "每个夜晚*，你要选择一名玩家和一个角色，如果该角色不在场，他变成该角色。如果因此创造了一个恶魔，当晚的死亡由说书人决定。"},
    ),
    "hadisyia": ScriptRole(
        id="hadisyia",
        name="Hadisyia",
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
    "ossuary_demon": ScriptRole(
        id="ossuary_demon",
        name="Ossuary Demon",
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
    "artist": ScriptRole(
        id="artist",
        name="Artist",
        team="townsfolk",
        tags=["limited-use", "day", "info"],
        name_localized={"zh_CN": "艺术家"},
        meta={"description": "每局游戏限一次，在白天时，你可以私下询问说书人一个是/否答案问题。"},
    ),
    "clockmaker": ScriptRole(
        id="clockmaker",
        name="Clockmaker",
        team="townsfolk",
        tags=["first-night", "info"],
        name_localized={"zh_CN": "钟表匠"},
        meta={"description": "在游戏开始时，你会得知恶魔与其最近爪牙之间的距离（1代表相邻）。"},
    ),
    "dreamer": ScriptRole(
        id="dreamer",
        name="Dreamer",
        team="townsfolk",
        tags=["nightly", "info"],
        name_localized={"zh_CN": "梦小者"},
        meta={"description": "每个夜晚，选择一名玩家（不能是自己或旅行者）；你会得知一个善良角色和一个邪恶角色，其中一个是正确的。"},
    ),
    "flowergirl": ScriptRole(
        id="flowergirl",
        name="Flowergirl",
        team="townsfolk",
        tags=["nightly", "info"],
        name_localized={"zh_CN": "卖花女"},
        meta={"description": "每个夜晚*，你会得知恶魔是否在白天投过票。"},
    ),
    "juggler": ScriptRole(
        id="juggler",
        name="Juggler",
        team="townsfolk",
        tags=["first-day", "info"],
        name_localized={"zh_CN": "杂耍者"},
        meta={"description": "在你的第一个白天，公开猜测至多5名玩家的角色。那个晚上，你能得知猜测正确的个数。"},
    ),
    "mathematician": ScriptRole(
        id="mathematician",
        name="Mathematician",
        team="townsfolk",
        tags=["nightly", "info"],
        name_localized={"zh_CN": "数学家"},
        meta={"description": "每个夜晚，你会得知今天白天和这个夜晚总共有多少名玩家的能力因其他角色的能力的影响而未能获得如愿的结果。"},
    ),
    "oracle": ScriptRole(
        id="oracle",
        name="Oracle",
        team="townsfolk",
        tags=["nightly", "info"],
        name_localized={"zh_CN": "神谕者"},
        meta={"description": "每个夜晚，你会得知死亡的玩家中有多少名是邪恶阵营的。"},
    ),
    "philosopher": ScriptRole(
        id="philosopher",
        name="Philosopher",
        team="townsfolk",
        tags=["limited-use", "nightly", "copy"],
        name_localized={"zh_CN": "哲学家"},
        meta={"description": "每局游戏限一次，在夜晚，挑选一个善良阵营的角色，获得该角色能力。如果该角色在场，则其持续醉酒。"},
    ),
    "sage": ScriptRole(
        id="sage",
        name="Sage",
        team="townsfolk",
        tags=["reaction", "info"],
        name_localized={"zh_CN": "贤者"},
        meta={"description": "如果恶魔杀死了你，你会得知两名玩家，其中一位是恶魔。"},
    ),
    "courtier": ScriptRole(
        id="courtier",
        name="Courtier",
        team="townsfolk",
        tags=["limited-use", "nightly", "info"],
        name_localized={"zh_CN": "裁缝"},
        meta={"description": "每局游戏限一次，在夜晚时，选择两名玩家（不能是自己）；你会得知他们是否属于同一阵营。"},
    ),
    "town_crier": ScriptRole(
        id="town_crier",
        name="Town Crier",
        team="townsfolk",
        tags=["nightly", "info"],
        name_localized={"zh_CN": "公告员"},
        meta={"description": "每个夜晚，你会得知是否有爪牙在今天发起了提名。"},
    ),
    "mutant": ScriptRole(
        id="mutant",
        name="Mutant",
        team="outsider",
        tags=["special", "madness"],
        name_localized={"zh_CN": "变种人"},
        meta={"description": "如果你“疯狂”地认为自己是外来者，那么你可能会立即被处决。"},
    ),
    "drunk_lover": ScriptRole(
        id="drunk_lover",
        name="Sweetheart",
        team="outsider",
        tags=["death_trigger", "drunk_effect"],
        name_localized={"zh_CN": "心上人"},
        meta={"description": "当你死亡时，一名其他玩家将持续醉酒。"},
    ),
    "fool": ScriptRole(
        id="fool",
        name="Fool",
        team="outsider",
        tags=["death_trigger", "risk"],
        name_localized={"zh_CN": "傻瓜"},
        meta={"description": "当你得知你的死亡时，公开选择一名活着的玩家；如果该玩家是邪恶的，你的阵营落败。"},
    ),
    "evil_twin": ScriptRole(
        id="evil_twin",
        name="Evil Twin",
        team="minion",
        tags=["pair", "knowledge", "win_condition"],
        name_localized={"zh_CN": "镜像双子"},
        meta={
            "description": "你和一个对立阵营的玩家相互认识。其中善良阵营的玩家被处决时，邪恶阵营直接获胜。双子都存活时，善良阵营玩家无法获胜。"
        },
    ),
    "cerenovus": ScriptRole(
        id="cerenovus",
        name="Cerenovus",
        team="minion",
        tags=["nightly", "madness"],
        name_localized={"zh_CN": "洗脑师"},
        meta={
            "description": "每个夜晚，你选择一名玩家和一个善良阵营角色；该玩家在次日必须“疯狂”地认为自己是该角色，否则可能会被立刻处决。"
        },
    ),
    "wizard": ScriptRole(
        id="wizard",
        name="Wizard",
        team="minion",
        tags=["nightly", "nomination_death", "limited"],
        name_localized={"zh_CN": "巫师"},
        meta={
            "description": "每个夜晚，你选择一名玩家；如果该玩家在第二天发起提名，则其死亡。如果仅剩 3 名玩家存活，你失去此能力。"
        },
    ),
    "pit_dreamer": ScriptRole(
        id="pit_dreamer",
        name="Pukka",
        team="demon",
        tags=["night_kill", "outsider_conversion"],
        name_localized={"zh_CN": "噩梦游魂"},
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
    "poison_god": ScriptRole(
        id="poison_god",
        name="Po",
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
    "whirlpool": ScriptRole(
        id="whirlpool",
        name="Vortex",
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
    "alchemist": ScriptRole(
        id="alchemist",
        name="Alchemist",
        team="minion",
        tags=["borrowed_ability"],
        name_localized={"zh_CN": "炼金术士"},
        meta={
            "description": "你拥有一个不在场的爪牙角色的能力。"
        },
    ),
    "general": ScriptRole(
        id="general",
        name="General",
        team="townsfolk",
        tags=["alignment_hint"],
        name_localized={"zh_CN": "将军"},
        meta={
            "description": "每个夜晚，你会得知说书人认为哪个阵营当前更有优势。（善良 / 邪恶 / 均势）"
        },
    ),
    "politician": ScriptRole(
        id="politician",
        name="Politician",
        team="townsfolk",
        tags=["alignment_shift", "special_win"],
        name_localized={"zh_CN": "政客"},
        meta={
            "description": "如果你是对你的阵营落败负最大责任的人，你转变阵营并获胜，即使你已死亡。"
        },
    ),
    "heretic": ScriptRole(
        id="heretic",
        name="Heretic",
        team="traveller",
        tags=["special_win"],
        name_localized={"zh_CN": "异端分子"},
        meta={
            "description": "对调胜负结果，即使你已死亡。"
        },
    ),
    "fear_spirit": ScriptRole(
        id="fear_spirit",
        name="Spirit of Fear",
        team="demon",
        tags=["night_action", "curse_link"],
        name_localized={"zh_CN": "恐惧之灵"},
        meta={
            "description": "每个夜晚，你要选择一名玩家；如果你提名的他被处决，他的阵营落败。当你首次选择或更换目标时，所有玩家都会得知你选择了新目标。"
        },
    ),
    "goblin": ScriptRole(
        id="goblin",
        name="Goblin",
        team="minion",
        tags=["public_announcement", "execution_win"],
        name_localized={"zh_CN": "哥布林"},
        meta={
            "description": "如果你在被提名后公开声明自己是哥布林且在那个白天被处决，你的阵营获胜。"
        },
    ),
    "leeches": ScriptRole(
        id="leeches",
        name="Leech",
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
