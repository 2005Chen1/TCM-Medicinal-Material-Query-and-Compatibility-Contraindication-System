"""
主程序入口 — 中医药常用药材查询与配伍禁忌系统。
自动初始化sqlite3数据库，载入内置测试数据，启动tkinter桌面GUI。

运行方式：python main.py
"""

import os
import sys

# 确保工作目录为项目根目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from database import DBManager
from data import SEED_HERBS, SEED_RULES
from ui import TCMApp


def main():
    """程序主入口：初始化数据库 → 载入种子数据 → 启动GUI。"""
    print("正在初始化中医药数据库...")
    db = DBManager()

    # 检查是否已有数据（首次运行导入种子数据）
    stats = db.get_statistics()
    if stats["herb_count"] == 0:
        print("首次运行，正在导入内置测试数据...")
        db.seed_data(SEED_HERBS, SEED_RULES)
        print(f"已导入 {len(SEED_HERBS)} 种药材，{len(SEED_RULES)} 条禁忌规则。")
    else:
        print(f"数据库已有 {stats['herb_count']} 种药材，{stats['rule_count']} 条规则。")

    print("正在启动GUI界面...")
    app = TCMApp(db)
    app.run()
    db.close()


if __name__ == "__main__":
    main()
