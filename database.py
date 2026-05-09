"""
数据库模块 — 使用Python内置sqlite3实现所有数据操作。
包含：建表、药材CRUD、配伍禁忌CRUD、模糊查询、统计、JSON导入导出。
"""

import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tcm.db")


class DBManager:
    """中医药数据库管理器，封装所有sqlite3操作。"""

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._init_tables()

    def _init_tables(self):
        """创建药材表和配伍禁忌表（如不存在）。"""
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS herbs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                pinyin TEXT DEFAULT '',
                alias TEXT DEFAULT '',
                xingwei TEXT DEFAULT '',
                guijing TEXT DEFAULT '',
                gongxiao TEXT DEFAULT '',
                category TEXT DEFAULT '',
                yongfa_yongliang TEXT DEFAULT '',
                laiyuan TEXT DEFAULT '',
                zhuyi TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS incompatibilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                herb_a TEXT NOT NULL,
                herb_b TEXT NOT NULL,
                rule_type TEXT DEFAULT '其它',
                description TEXT DEFAULT '',
                UNIQUE(herb_a, herb_b)
            );
        """)
        self.conn.commit()

    # ======================== 药材 CRUD ========================

    def add_herb(self, data: dict) -> int:
        """添加药材，返回新记录的id。name重复时返回-1。"""
        try:
            cur = self.conn.execute(
                """INSERT INTO herbs (name, pinyin, alias, xingwei, guijing,
                   gongxiao, category, yongfa_yongliang, laiyuan, zhuyi)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (data["name"], data.get("pinyin", ""), data.get("alias", ""),
                 data.get("xingwei", ""), data.get("guijing", ""),
                 data.get("gongxiao", ""), data.get("category", ""),
                 data.get("yongfa_yongliang", ""), data.get("laiyuan", ""),
                 data.get("zhuyi", ""))
            )
            self.conn.commit()
            return cur.lastrowid
        except sqlite3.IntegrityError:
            return -1

    def update_herb(self, herb_id: int, data: dict) -> bool:
        """更新药材信息。"""
        fields = ["name", "pinyin", "alias", "xingwei", "guijing",
                  "gongxiao", "category", "yongfa_yongliang", "laiyuan", "zhuyi"]
        sets = [f"{f}=?" for f in fields]
        values = [data.get(f, "") for f in fields]
        values.append(herb_id)
        cur = self.conn.execute(
            f"UPDATE herbs SET {', '.join(sets)} WHERE id=?",
            values
        )
        self.conn.commit()
        return cur.rowcount > 0

    def delete_herb(self, herb_id: int) -> bool:
        """删除药材。"""
        cur = self.conn.execute("DELETE FROM herbs WHERE id=?", (herb_id,))
        self.conn.commit()
        return cur.rowcount > 0

    def get_herb(self, herb_id: int) -> dict | None:
        """按id获取单个药材。"""
        row = self.conn.execute(
            "SELECT * FROM herbs WHERE id=?", (herb_id,)
        ).fetchone()
        return dict(row) if row else None

    def get_all_herbs(self) -> list[dict]:
        """获取全部药材列表。"""
        rows = self.conn.execute(
            "SELECT id, name, pinyin, category, gongxiao FROM herbs ORDER BY id"
        ).fetchall()
        return [dict(r) for r in rows]

    def get_herb_by_name(self, name: str) -> dict | None:
        """按名称精确查找药材。"""
        row = self.conn.execute(
            "SELECT * FROM herbs WHERE name=?", (name,)
        ).fetchone()
        return dict(row) if row else None

    # ======================== 模糊查询 ========================

    def search_herbs(self, keyword: str, field: str = "name") -> list[dict]:
        """按指定字段模糊查询药材。field: name/pinyin/category/gongxiao。"""
        allowed = {"name", "pinyin", "category", "gongxiao", "alias"}
        if field not in allowed:
            field = "name"
        pattern = f"%{keyword}%"
        rows = self.conn.execute(
            f"SELECT * FROM herbs WHERE {field} LIKE ? ORDER BY id",
            (pattern,)
        ).fetchall()
        return [dict(r) for r in rows]

    # ======================== 配伍禁忌 CRUD ========================

    def add_rule(self, herb_a: str, herb_b: str,
                 rule_type: str = "其它", description: str = "") -> int:
        """添加配伍禁忌规则。"""
        a, b = sorted([herb_a.strip(), herb_b.strip()])
        try:
            cur = self.conn.execute(
                """INSERT INTO incompatibilities (herb_a, herb_b, rule_type, description)
                   VALUES (?, ?, ?, ?)""",
                (a, b, rule_type, description)
            )
            self.conn.commit()
            return cur.lastrowid
        except sqlite3.IntegrityError:
            return -1

    def update_rule(self, rule_id: int, herb_a: str, herb_b: str,
                    rule_type: str, description: str) -> bool:
        """更新配伍禁忌规则。"""
        a, b = sorted([herb_a.strip(), herb_b.strip()])
        cur = self.conn.execute(
            """UPDATE incompatibilities
               SET herb_a=?, herb_b=?, rule_type=?, description=?
               WHERE id=?""",
            (a, b, rule_type, description, rule_id)
        )
        self.conn.commit()
        return cur.rowcount > 0

    def delete_rule(self, rule_id: int) -> bool:
        """删除配伍禁忌规则。"""
        cur = self.conn.execute(
            "DELETE FROM incompatibilities WHERE id=?", (rule_id,)
        )
        self.conn.commit()
        return cur.rowcount > 0

    def get_all_rules(self) -> list[dict]:
        """获取全部禁忌规则。"""
        rows = self.conn.execute(
            "SELECT * FROM incompatibilities ORDER BY rule_type, id"
        ).fetchall()
        return [dict(r) for r in rows]

    # ======================== 配伍禁忌检查 ========================

    def check_incompatibility(self, herb_names: list[str]) -> list[dict]:
        """检查多味药材之间是否存在配伍禁忌。
        返回所有冲突规则列表，每条规则附带匹配的药材对。
        """
        results = []
        names = [n.strip() for n in herb_names if n.strip()]
        if len(names) < 2:
            return results

        rules = self.get_all_rules()
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = sorted([names[i], names[j]])
                for rule in rules:
                    ra, rb = sorted([rule["herb_a"], rule["herb_b"]])
                    if a == ra and b == rb:
                        results.append({
                            "herb_1": names[i],
                            "herb_2": names[j],
                            "rule_type": rule["rule_type"],
                            "description": rule["description"]
                        })
        return results

    # ======================== 统计 ========================

    def get_statistics(self) -> dict:
        """返回统计信息：药材总数、禁忌组数、各分类数量、各禁忌类型数量。"""
        herb_count = self.conn.execute(
            "SELECT COUNT(*) FROM herbs"
        ).fetchone()[0]
        rule_count = self.conn.execute(
            "SELECT COUNT(*) FROM incompatibilities"
        ).fetchone()[0]
        categories = self.conn.execute(
            "SELECT category, COUNT(*) as cnt FROM herbs "
            "WHERE category != '' GROUP BY category ORDER BY cnt DESC"
        ).fetchall()
        rule_types = self.conn.execute(
            "SELECT rule_type, COUNT(*) as cnt FROM incompatibilities "
            "GROUP BY rule_type ORDER BY cnt DESC"
        ).fetchall()
        return {
            "herb_count": herb_count,
            "rule_count": rule_count,
            "categories": [(r["category"], r["cnt"]) for r in categories],
            "rule_types": [(r["rule_type"], r["cnt"]) for r in rule_types],
        }

    # ======================== JSON 导入导出 ========================

    def export_to_json(self, filepath: str) -> int:
        """导出全部数据为JSON文件。返回导出的记录总数。"""
        herbs = [dict(r) for r in self.conn.execute(
            "SELECT * FROM herbs ORDER BY id"
        ).fetchall()]
        rules = [dict(r) for r in self.conn.execute(
            "SELECT * FROM incompatibilities ORDER BY id"
        ).fetchall()]
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({"herbs": herbs, "incompatibilities": rules},
                      f, ensure_ascii=False, indent=2)
        return len(herbs) + len(rules)

    def import_from_json(self, filepath: str) -> tuple[int, int]:
        """从JSON文件导入数据。返回(导入药材数, 导入规则数)。"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        herb_count = 0
        for h in data.get("herbs", []):
            hid = self.add_herb(h)
            if hid > 0:
                herb_count += 1

        rule_count = 0
        for r in data.get("incompatibilities", []):
            rid = self.add_rule(
                r["herb_a"], r["herb_b"],
                r.get("rule_type", "其它"),
                r.get("description", "")
            )
            if rid > 0:
                rule_count += 1

        return herb_count, rule_count

    # ======================== 数据库重置 ========================

    def reset_database(self):
        """清空所有数据并重建表结构。"""
        self.conn.executescript("""
            DROP TABLE IF EXISTS incompatibilities;
            DROP TABLE IF EXISTS herbs;
        """)
        self.conn.commit()
        self._init_tables()

    # ======================== 批量导入种子数据 ========================

    def seed_data(self, herbs: list[dict], rules: list[dict]):
        """批量导入种子数据（事务保护）。"""
        try:
            for h in herbs:
                self.add_herb(h)
            for r in rules:
                self.add_rule(
                    r["herb_a"], r["herb_b"],
                    r.get("rule_type", "其它"),
                    r.get("description", "")
                )
        except Exception:
            self.conn.rollback()
            raise

    def close(self):
        """关闭数据库连接。"""
        if self.conn:
            self.conn.close()
