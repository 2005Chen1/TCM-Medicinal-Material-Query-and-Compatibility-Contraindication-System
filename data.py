"""
数据模块 — 内置中药材基础数据与配伍禁忌规则。
覆盖常见药材及中医"十八反""十九畏"核心禁忌。
"""

# ======================== 药材种子数据 ========================

SEED_HERBS = [
    {
        "name": "甘草", "pinyin": "gancao", "alias": "国老、甜草",
        "xingwei": "甘，平", "guijing": "心、肺、脾、胃",
        "gongxiao": "补脾益气、清热解毒、祛痰止咳、缓急止痛、调和诸药",
        "category": "补气药",
        "yongfa_yongliang": "煎服，2~10g。清热解毒宜生用，补中缓急宜炙用",
        "laiyuan": "豆科植物甘草、胀果甘草或光果甘草的干燥根及根茎",
        "zhuyi": "不宜与甘遂、大戟、芫花、海藻同用。湿盛胀满、水肿者慎用"
    },
    {
        "name": "人参", "pinyin": "renshen", "alias": "棒槌、山参、园参",
        "xingwei": "甘、微苦，微温", "guijing": "脾、肺、心、肾",
        "gongxiao": "大补元气、复脉固脱、补脾益肺、生津养血、安神益智",
        "category": "补气药",
        "yongfa_yongliang": "煎服，3~9g。另煎兑服。挽救虚脱可用15~30g",
        "laiyuan": "五加科植物人参的干燥根及根茎",
        "zhuyi": "不宜与藜芦、五灵脂同用。实证、热证而正气不虚者忌服"
    },
    {
        "name": "黄芪", "pinyin": "huangqi", "alias": "黄耆、北芪",
        "xingwei": "甘，温", "guijing": "肺、脾",
        "gongxiao": "补气升阳、固表止汗、利水消肿、生津养血、行滞通痹",
        "category": "补气药",
        "yongfa_yongliang": "煎服，9~30g",
        "laiyuan": "豆科植物蒙古黄芪或膜荚黄芪的干燥根",
        "zhuyi": "表实邪盛、气滞湿阻、痈疽初起或溃后热毒尚盛者慎用"
    },
    {
        "name": "当归", "pinyin": "danggui", "alias": "秦归、云归、西当归",
        "xingwei": "甘、辛，温", "guijing": "肝、心、脾",
        "gongxiao": "补血活血、调经止痛、润肠通便",
        "category": "补血药",
        "yongfa_yongliang": "煎服，6~12g",
        "laiyuan": "伞形科植物当归的干燥根",
        "zhuyi": "湿盛中满、大便溏泄者慎用"
    },
    {
        "name": "枸杞子", "pinyin": "gouqizi", "alias": "杞子、枸杞、红耳坠",
        "xingwei": "甘，平", "guijing": "肝、肾",
        "gongxiao": "滋补肝肾、益精明目",
        "category": "补阴药",
        "yongfa_yongliang": "煎服，6~12g",
        "laiyuan": "茄科植物宁夏枸杞的干燥成熟果实",
        "zhuyi": "外邪实热、脾虚有湿及泄泻者慎用"
    },
    {
        "name": "大黄", "pinyin": "dahuang", "alias": "将军、川军、锦纹",
        "xingwei": "苦，寒", "guijing": "脾、胃、大肠、肝、心包",
        "gongxiao": "泻下攻积、清热泻火、凉血解毒、逐瘀通经、利湿退黄",
        "category": "泻下药",
        "yongfa_yongliang": "煎服，3~15g。外用适量。生大黄泻下力强",
        "laiyuan": "蓼科植物掌叶大黄、唐古特大黄或药用大黄的干燥根及根茎",
        "zhuyi": "孕妇及月经期、哺乳期慎用。脾胃虚寒者忌用"
    },
    {
        "name": "黄连", "pinyin": "huanglian", "alias": "味连、川连、鸡爪连",
        "xingwei": "苦，寒", "guijing": "心、脾、胃、肝、胆、大肠",
        "gongxiao": "清热燥湿、泻火解毒",
        "category": "清热药",
        "yongfa_yongliang": "煎服，2~5g。外用适量",
        "laiyuan": "毛茛科植物黄连、三角叶黄连或云连的干燥根茎",
        "zhuyi": "脾胃虚寒者忌用。阴虚津伤者慎用"
    },
    {
        "name": "半夏", "pinyin": "banxia", "alias": "三叶半夏、地文、守田",
        "xingwei": "辛，温；有毒", "guijing": "脾、胃、肺",
        "gongxiao": "燥湿化痰、降逆止呕、消痞散结",
        "category": "化痰止咳平喘药",
        "yongfa_yongliang": "煎服，3~9g。内服一般宜制用",
        "laiyuan": "天南星科植物半夏的干燥块茎",
        "zhuyi": "不宜与川乌、草乌、附子同用（十八反）。阴虚燥咳、血证者慎用"
    },
    {
        "name": "川贝母", "pinyin": "chuanbeimu", "alias": "川贝、贝母",
        "xingwei": "苦、甘，微寒", "guijing": "肺、心",
        "gongxiao": "清热润肺、化痰止咳、散结消痈",
        "category": "化痰止咳平喘药",
        "yongfa_yongliang": "煎服，3~9g；研粉冲服，一次1~2g",
        "laiyuan": "百合科植物川贝母、暗紫贝母、甘肃贝母等的干燥鳞茎",
        "zhuyi": "不宜与川乌、草乌、附子同用（十八反）"
    },
    {
        "name": "茯苓", "pinyin": "fuling", "alias": "云苓、茯菟、松苓",
        "xingwei": "甘、淡，平", "guijing": "心、肺、脾、肾",
        "gongxiao": "利水渗湿、健脾宁心",
        "category": "利水渗湿药",
        "yongfa_yongliang": "煎服，10~15g",
        "laiyuan": "多孔菌科真菌茯苓的干燥菌核",
        "zhuyi": "阴虚而无湿热、虚寒滑精者慎用"
    },
    {
        "name": "丹参", "pinyin": "danshen", "alias": "赤参、紫丹参、红根",
        "xingwei": "苦，微寒", "guijing": "心、肝",
        "gongxiao": "活血祛瘀、通经止痛、清心除烦、凉血消痈",
        "category": "活血化瘀药",
        "yongfa_yongliang": "煎服，10~15g",
        "laiyuan": "唇形科植物丹参的干燥根及根茎",
        "zhuyi": "不宜与藜芦同用（十八反）。孕妇慎用"
    },
    {
        "name": "川芎", "pinyin": "chuanxiong", "alias": "芎藭、西川芎",
        "xingwei": "辛，温", "guijing": "肝、胆、心包",
        "gongxiao": "活血行气、祛风止痛",
        "category": "活血化瘀药",
        "yongfa_yongliang": "煎服，3~10g",
        "laiyuan": "伞形科植物川芎的干燥根茎",
        "zhuyi": "阴虚火旺、多汗者慎用。月经过多及孕妇慎用"
    },
    {
        "name": "陈皮", "pinyin": "chenpi", "alias": "橘皮、广陈皮、新会皮",
        "xingwei": "苦、辛，温", "guijing": "肺、脾",
        "gongxiao": "理气健脾、燥湿化痰",
        "category": "理气药",
        "yongfa_yongliang": "煎服，3~10g",
        "laiyuan": "芸香科植物橘及其栽培变种的干燥成熟果皮",
        "zhuyi": "内有实热、阴虚燥咳者慎用"
    },
    {
        "name": "金银花", "pinyin": "jinyinhua", "alias": "忍冬花、双花、二花",
        "xingwei": "甘，寒", "guijing": "肺、心、胃",
        "gongxiao": "清热解毒、疏散风热",
        "category": "清热药",
        "yongfa_yongliang": "煎服，6~15g",
        "laiyuan": "忍冬科植物忍冬的干燥花蕾或带初开的花",
        "zhuyi": "脾胃虚寒及气虚疮疡脓清者慎用"
    },
    {
        "name": "附子", "pinyin": "fuzi", "alias": "附片、黑顺片、白附片",
        "xingwei": "辛、甘，大热；有毒", "guijing": "心、肾、脾",
        "gongxiao": "回阳救逆、补火助阳、散寒止痛",
        "category": "温里药",
        "yongfa_yongliang": "煎服，3~15g。宜先煎、久煎（60分钟以上）以减毒",
        "laiyuan": "毛茛科植物乌头的子根加工品",
        "zhuyi": "不宜与半夏、瓜蒌、贝母、白蔹、白及同用（十八反）。孕妇忌用"
    },
    {
        "name": "白芍", "pinyin": "baishao", "alias": "芍药、金芍药",
        "xingwei": "苦、酸，微寒", "guijing": "肝、脾",
        "gongxiao": "养血调经、敛阴止汗、柔肝止痛、平抑肝阳",
        "category": "补血药",
        "yongfa_yongliang": "煎服，6~15g",
        "laiyuan": "毛茛科植物芍药的干燥根",
        "zhuyi": "不宜与藜芦同用（十八反）。虚寒腹痛泄泻者慎用"
    },
    {
        "name": "桂枝", "pinyin": "guizhi", "alias": "桂尖、柳桂",
        "xingwei": "辛、甘，温", "guijing": "心、肺、膀胱",
        "gongxiao": "发汗解表、温通经脉、助阳化气、平冲降逆",
        "category": "解表药",
        "yongfa_yongliang": "煎服，3~10g",
        "laiyuan": "樟科植物肉桂的干燥嫩枝",
        "zhuyi": "外感热病、阴虚火旺、血热妄行者忌用"
    },
    {
        "name": "菊花", "pinyin": "juhua", "alias": "白菊花、甘菊花、滁菊",
        "xingwei": "甘、苦，微寒", "guijing": "肺、肝",
        "gongxiao": "散风清热、平肝明目、清热解毒",
        "category": "解表药",
        "yongfa_yongliang": "煎服，5~10g",
        "laiyuan": "菊科植物菊的干燥头状花序",
        "zhuyi": "气虚胃寒、食少泄泻者慎用"
    },
    {
        "name": "甘遂", "pinyin": "gansui", "alias": "猫儿眼、肿手花",
        "xingwei": "苦，寒；有毒", "guijing": "肺、肾、大肠",
        "gongxiao": "泻水逐饮、消肿散结",
        "category": "泻下药",
        "yongfa_yongliang": "炮制后多入丸散用，每次0.5~1.5g。外用适量",
        "laiyuan": "大戟科植物甘遂的干燥块根",
        "zhuyi": "不宜与甘草同用（十八反）。孕妇及体虚者忌用"
    },
    {
        "name": "藜芦", "pinyin": "lilu", "alias": "山葱、黑藜芦",
        "xingwei": "苦、辛，寒；有毒", "guijing": "肺、胃、肝",
        "gongxiao": "涌吐风痰、杀虫疗疮",
        "category": "涌吐药",
        "yongfa_yongliang": "内服0.3~0.9g，入丸散。外用适量",
        "laiyuan": "百合科植物藜芦的干燥根及根茎",
        "zhuyi": "不宜与人参、沙参、丹参、玄参、细辛、芍药同用（十八反）。孕妇忌用"
    },
    {
        "name": "丁香", "pinyin": "dingxiang", "alias": "公丁香、丁子香",
        "xingwei": "辛，温", "guijing": "脾、胃、肺、肾",
        "gongxiao": "温中降逆、补肾助阳",
        "category": "温里药",
        "yongfa_yongliang": "煎服，1~3g。外用适量",
        "laiyuan": "桃金娘科植物丁香的干燥花蕾",
        "zhuyi": "不宜与郁金同用（十九畏）。热证及阴虚内热者忌用"
    },
    {
        "name": "郁金", "pinyin": "yujin", "alias": "黄郁金、广郁金",
        "xingwei": "辛、苦，寒", "guijing": "肝、心、肺",
        "gongxiao": "活血止痛、行气解郁、清心凉血、利胆退黄",
        "category": "活血化瘀药",
        "yongfa_yongliang": "煎服，3~10g",
        "laiyuan": "姜科植物温郁金、姜黄、广西莪术或蓬莪术的干燥块根",
        "zhuyi": "不宜与丁香同用（十九畏）。孕妇慎用"
    },
    {
        "name": "巴豆", "pinyin": "badou", "alias": "巴菽、江子、刚子",
        "xingwei": "辛，热；有大毒", "guijing": "胃、大肠",
        "gongxiao": "峻下冷积、逐水退肿、豁痰利咽",
        "category": "泻下药",
        "yongfa_yongliang": "制霜入丸散，0.1~0.3g。外用适量",
        "laiyuan": "大戟科植物巴豆的干燥成熟果实",
        "zhuyi": "不宜与牵牛子同用（十九畏）。孕妇及体弱者忌用"
    },
    {
        "name": "牵牛子", "pinyin": "qianniuzi", "alias": "黑丑、白丑、二丑",
        "xingwei": "苦，寒；有毒", "guijing": "肺、肾、大肠",
        "gongxiao": "泻下逐水、去积杀虫",
        "category": "泻下药",
        "yongfa_yongliang": "煎服，3~6g。入丸散每次1.5~3g",
        "laiyuan": "旋花科植物裂叶牵牛或圆叶牵牛的干燥成熟种子",
        "zhuyi": "不宜与巴豆同用（十九畏）。孕妇及胃弱气虚者忌用"
    },
    {
        "name": "麻黄", "pinyin": "mahuang", "alias": "龙沙、狗骨、色道麻",
        "xingwei": "辛、微苦，温", "guijing": "肺、膀胱",
        "gongxiao": "发汗解表、宣肺平喘、利水消肿",
        "category": "解表药",
        "yongfa_yongliang": "煎服，2~10g。发汗解表宜生用，止咳平喘多炙用",
        "laiyuan": "麻黄科植物草麻黄、中麻黄或木贼麻黄的干燥草质茎",
        "zhuyi": "表虚自汗、阴虚盗汗及肺肾虚喘者慎用"
    },
]

# ======================== 配伍禁忌种子数据 ========================

SEED_RULES = [
    # ---------- 十八反 ----------
    {"herb_a": "甘草", "herb_b": "甘遂",
     "rule_type": "十八反",
     "description": "甘草反甘遂。两药合用可增强毒副作用。藻戟遂芫俱战草。"},
    {"herb_a": "甘草", "herb_b": "大戟",
     "rule_type": "十八反",
     "description": "甘草反大戟。两药合用可增强毒副作用。"},
    {"herb_a": "甘草", "herb_b": "芫花",
     "rule_type": "十八反",
     "description": "甘草反芫花。两药合用可增强毒副作用。"},
    {"herb_a": "甘草", "herb_b": "海藻",
     "rule_type": "十八反",
     "description": "甘草反海藻。两药合用可增强毒副作用。藻戟遂芫俱战草。"},

    {"herb_a": "川乌", "herb_b": "川贝母",
     "rule_type": "十八反",
     "description": "乌头反贝母。半蒌贝蔹及攻乌。"},
    {"herb_a": "川乌", "herb_b": "瓜蒌",
     "rule_type": "十八反",
     "description": "乌头反瓜蒌。半蒌贝蔹及攻乌。"},
    {"herb_a": "川乌", "herb_b": "半夏",
     "rule_type": "十八反",
     "description": "乌头反半夏。半蒌贝蔹及攻乌。"},
    {"herb_a": "川乌", "herb_b": "白蔹",
     "rule_type": "十八反",
     "description": "乌头反白蔹。半蒌贝蔹及攻乌。"},
    {"herb_a": "川乌", "herb_b": "白及",
     "rule_type": "十八反",
     "description": "乌头反白及。半蒌贝蔹及攻乌。"},

    {"herb_a": "附子", "herb_b": "半夏",
     "rule_type": "十八反",
     "description": "附子与半夏属十八反范畴。乌头类（含附子）不宜与半夏同用。"},
    {"herb_a": "附子", "herb_b": "川贝母",
     "rule_type": "十八反",
     "description": "附子与贝母属十八反范畴。乌头类（含附子）不宜与贝母同用。"},

    {"herb_a": "藜芦", "herb_b": "人参",
     "rule_type": "十八反",
     "description": "藜芦反人参。诸参辛芍叛藜芦。"},
    {"herb_a": "藜芦", "herb_b": "丹参",
     "rule_type": "十八反",
     "description": "藜芦反丹参。诸参辛芍叛藜芦。"},
    {"herb_a": "藜芦", "herb_b": "白芍",
     "rule_type": "十八反",
     "description": "藜芦反芍药。诸参辛芍叛藜芦。"},

    # ---------- 十九畏 ----------
    {"herb_a": "丁香", "herb_b": "郁金",
     "rule_type": "十九畏",
     "description": "丁香莫与郁金见。两药合用可降低药效或产生不良反应。"},
    {"herb_a": "巴豆", "herb_b": "牵牛子",
     "rule_type": "十九畏",
     "description": "巴豆性烈最为上，偏与牵牛不顺情。两药合用增强毒性。"},
    {"herb_a": "人参", "herb_b": "五灵脂",
     "rule_type": "十九畏",
     "description": "人参畏五灵脂。两药合用可降低人参补气效果，属配伍禁忌。"},
]
