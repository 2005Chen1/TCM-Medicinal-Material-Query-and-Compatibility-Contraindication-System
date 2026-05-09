"""
测试模块 — 中医药常用药材查询与配伍禁忌系统测试用例。
运行方式：python test.py
覆盖：数据库初始化、药材CRUD、模糊查询、配伍禁忌检查、导入导出、统计。
"""

import os
import sys
import json
import tempfile

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from database import DBManager
from data import SEED_HERBS, SEED_RULES

# 使用临时数据库进行测试，不影响正式数据
TEST_DB = os.path.join(tempfile.gettempdir(), "tcm_test.db")


def setup_module():
    """测试前准备：创建测试数据库并导入种子数据。"""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    db = DBManager(TEST_DB)
    db.seed_data(SEED_HERBS, SEED_RULES)
    return db


def teardown_module(db):
    """测试后清理：关闭连接并删除测试数据库。"""
    db.close()
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def run_tests():
    """运行全部测试用例，打印结果。"""
    passed = 0
    failed = 0
    results = []

    def check(desc, condition, detail=""):
        nonlocal passed, failed
        if condition:
            passed += 1
            results.append(f"  [PASS] {desc}")
        else:
            failed += 1
            results.append(f"  [FAIL] {desc}  FAILED: {detail}")

    print("=" * 55)
    print("  中医药常用药材查询与配伍禁忌系统 — 测试套件")
    print("=" * 55)

    db = setup_module()
    print(f"\n测试数据库：{TEST_DB}\n")

    # ==================== 测试用例1：数据库初始化 ====================
    print("【测试1】数据库初始化与种子数据载入")
    stats = db.get_statistics()
    check("种子数据导入成功（药材数>0）", stats["herb_count"] > 0,
          f"当前药材数: {stats['herb_count']}")
    check("禁忌规则导入成功（规则数>0）", stats["rule_count"] > 0,
          f"当前规则数: {stats['rule_count']}")
    check("药材总数≥25", stats["herb_count"] >= 25,
          f"实际: {stats['herb_count']}")

    # ==================== 测试用例2：药材CRUD ====================
    print("\n【测试2】药材增删改查操作")

    # 新增
    new_id = db.add_herb({
        "name": "测试药材", "pinyin": "ceshiyaocai",
        "xingwei": "甘，平", "guijing": "肝", "gongxiao": "测试功效",
        "category": "测试类", "yongfa_yongliang": "1~3g", "laiyuan": "测试来源"
    })
    check("新增药材成功（返回有效id）", new_id > 0, f"id={new_id}")

    # 重复添加
    dup_id = db.add_herb({"name": "测试药材"})
    check("重复名称拒绝添加", dup_id == -1, f"返回: {dup_id}")

    # 查询
    herb = db.get_herb(new_id)
    check("按id查询成功", herb is not None and herb["name"] == "测试药材")

    # 更新
    ok = db.update_herb(new_id, {"name": "测试药材", "pinyin": "ceshiyaocai",
                                  "gongxiao": "更新后的功效"})
    check("更新药材成功", ok)
    herb = db.get_herb(new_id)
    check("更新后查询字段正确", herb["gongxiao"] == "更新后的功效")

    # 删除
    ok = db.delete_herb(new_id)
    check("删除药材成功", ok)
    herb = db.get_herb(new_id)
    check("删除后查询为空", herb is None)

    # ==================== 测试用例3：模糊查询 ====================
    print("\n【测试3】药材模糊查询功能")

    results = db.search_herbs("甘", "name")
    check("按名称模糊查询'甘'有结果", len(results) > 0,
          f"匹配: {len(results)}条")

    results = db.search_herbs("补气", "gongxiao")
    check("按功效模糊查询'补气'有结果", len(results) > 0,
          f"匹配: {len(results)}条")

    results = db.search_herbs("renshen", "pinyin")
    check("按拼音查询'renshen'精确匹配", len(results) == 1 and results[0]["name"] == "人参")

    results = db.search_herbs("清热", "gongxiao")
    check("按功效查'清热'至少匹配到黄连、金银花",
          any("黄连" in r["name"] for r in results) and
          any("金银花" in r["name"] for r in results))

    # ==================== 测试用例4：配伍禁忌检查 ====================
    print("\n【测试4】配伍禁忌检查")

    # 已知禁忌对
    conflicts = db.check_incompatibility(["甘草", "甘遂"])
    check("甘草+甘遂检测到禁忌（十八反）", len(conflicts) > 0,
          f"冲突数: {len(conflicts)}")
    if conflicts:
        check("返回正确的禁忌类型", conflicts[0]["rule_type"] == "十八反",
              f"类型: {conflicts[0]['rule_type']}")

    # 无禁忌对
    conflicts = db.check_incompatibility(["当归", "枸杞子"])
    check("当归+枸杞子无禁忌", len(conflicts) == 0)

    # 三味药材
    conflicts = db.check_incompatibility(["甘草", "甘遂", "当归"])
    check("三味药材检查：甘草+甘遂触发禁忌", len(conflicts) >= 1)
    check("三味药材检查：当归不参与禁忌", len(conflicts) == 1)

    # 藜芦反人参
    conflicts = db.check_incompatibility(["藜芦", "人参"])
    check("藜芦+人参检测到禁忌（十八反）", len(conflicts) > 0)

    # 丁香畏郁金
    conflicts = db.check_incompatibility(["丁香", "郁金"])
    check("丁香+郁金检测到禁忌（十九畏）", len(conflicts) > 0)

    # 十九畏：巴豆+牵牛子
    conflicts = db.check_incompatibility(["巴豆", "牵牛子"])
    check("巴豆+牵牛子检测到禁忌（十九畏）", len(conflicts) > 0)

    # ==================== 测试用例5：禁忌规则管理 ====================
    print("\n【测试5】禁忌规则增删改")

    rid = db.add_rule("测试A", "测试B", "其它", "测试规则")
    check("新增禁忌规则成功", rid > 0)

    dup_rid = db.add_rule("测试A", "测试B")
    check("重复规则拒绝添加", dup_rid == -1)

    # 更新
    ok = db.update_rule(rid, "测试A", "测试B", "十九畏", "更新后的说明")
    check("更新规则成功", ok)

    # 删除
    ok = db.delete_rule(rid)
    check("删除规则成功", ok)

    # 对称输入测试
    rid = db.add_rule("药材X", "药材Y")
    conflicts = db.check_incompatibility(["药材X", "药材Y"])
    check("正序药材对检测到禁忌", len(conflicts) > 0)

    # 注意：check_incompatibility中使用sorted名称比较，所以只需要检查命名一致性
    ok = db.delete_rule(rid)
    conflicts = db.check_incompatibility(["药材X", "药材Y"])
    check("删除后不再检测到禁忌", len(conflicts) == 0)

    # ==================== 测试用例6：数据导入导出 ====================
    print("\n【测试6】JSON数据导入导出")

    export_path = os.path.join(tempfile.gettempdir(), "tcm_export_test.json")
    count = db.export_to_json(export_path)
    check("导出成功（记录数>0）", count > 0, f"导出: {count}条")
    check("导出文件存在", os.path.exists(export_path))

    # 验证导出文件格式
    with open(export_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    check("导出JSON包含herbs字段", "herbs" in data)
    check("导出JSON包含incompatibilities字段", "incompatibilities" in data)

    # 导入到新数据库
    TEST_DB2 = os.path.join(tempfile.gettempdir(), "tcm_test2.db")
    db2 = DBManager(TEST_DB2)
    hc, rc = db2.import_from_json(export_path)
    check("导入药材数匹配", hc == len(data["herbs"]),
          f"{hc} vs {len(data['herbs'])}")
    check("导入规则数匹配", rc == len(data["incompatibilities"]),
          f"{rc} vs {len(data['incompatibilities'])}")
    db2.close()
    os.remove(TEST_DB2)

    # 清理
    os.remove(export_path)

    # ==================== 测试用例7：统计功能 ====================
    print("\n【测试7】数据统计功能")

    stats = db.get_statistics()
    check("统计结果包含herb_count", "herb_count" in stats)
    check("统计结果包含rule_count", "rule_count" in stats)
    check("统计结果包含categories", "categories" in stats)
    check("统计结果包含rule_types", "rule_types" in stats)
    check("药材总数≥25", stats["herb_count"] >= 25,
          f"实际: {stats['herb_count']}")
    check("分类统计非空", len(stats["categories"]) > 0,
          f"分类数: {len(stats['categories'])}")

    # ==================== 测试用例8：数据库重置 ====================
    print("\n【测试8】数据库重置功能")

    db.reset_database()
    stats = db.get_statistics()
    check("重置后药材数为0", stats["herb_count"] == 0,
          f"实际: {stats['herb_count']}")
    check("重置后规则数为0", stats["rule_count"] == 0,
          f"实际: {stats['rule_count']}")

    # 重新导入种子数据
    db.seed_data(SEED_HERBS, SEED_RULES)
    stats = db.get_statistics()
    check("重新导入后药材恢复", stats["herb_count"] == len(SEED_HERBS),
          f"{stats['herb_count']} vs {len(SEED_HERBS)}")
    check("重新导入后规则恢复", stats["rule_count"] == len(SEED_RULES),
          f"{stats['rule_count']} vs {len(SEED_RULES)}")

    # ==================== 测试总结 ====================
    print("\n" + "=" * 55)
    total = passed + failed
    print(f"  测试结果：{passed}/{total} 通过", end="")
    if failed > 0:
        print(f"，{failed} 失败")
    else:
        print(" [PASS] 全部通过")
    print("=" * 55)

    for r in results:
        print(r)

    teardown_module(db)
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
