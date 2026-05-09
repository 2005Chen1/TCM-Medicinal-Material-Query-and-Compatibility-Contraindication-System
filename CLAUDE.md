# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

南京中医药大学《软件工程综合实践》课程设计项目 — 中医药常用药材查询与配伍禁忌系统。纯Python实现，零第三方依赖。

## Commands

```bash
python main.py    # 启动桌面GUI应用
python test.py    # 运行测试套件（使用临时数据库，不影响正式数据）
```

## Architecture

```
main.py          # 入口：DBManager初始化 → 首次运行导入种子数据 → 启动TCMApp GUI
database.py      # 数据层：sqlite3封装，DBManager类包含全部CRUD + 统计 + JSON导入导出
ui.py            # 表现层：tkinter GUI，TCMApp类包含6个Tab（药材管理/查询/配伍检查/规则管理/统计/数据操作）
data.py          # 种子数据：SEED_HERBS(25种药材) + SEED_RULES(17条十八反/十九畏规则)
test.py          # 测试套件：8大场景30+断言，使用tempfile临时数据库，不污染tcm.db
```

导入关系：`database.py` ← `main.py`, `ui.py`, `test.py`；`data.py` ← `main.py`, `test.py`；`ui.py` ← `main.py`。

数据库：`tcm.db`（自动创建），2张表 `herbs`（10字段+UNIQUE name）和 `incompatibilities`（herb_a, herb_b, rule_type, description，UNIQUE(herb_a, herb_b)）。

## Key Design Decisions

- **零依赖**：只用Python内置库（sqlite3, tkinter, json），无需pip install
- **测试隔离**：test.py在tempfile临时目录创建独立数据库，不影响生产数据
- **`os.chdir` 保证工作目录**：main.py和test.py都在入口处执行 `os.chdir(os.path.dirname(os.path.abspath(__file__)))`，确保相对路径（`tcm.db`、模块导入）从项目根目录解析
- **配伍禁忌检查**：`check_incompatibility()` 在Python层做名称匹配（非数据库JOIN），输入名称会排序后与规则比较，支持任意顺序输入；添加规则时 `add_rule()` 内部也会对herb_a/herb_b排序存储
- **首次运行**：main.py检测herb_count==0时自动导入data.py中的种子数据
- **数据表单**：ui.py中表单使用tk.Text（非Entry），多行字段（gongxiao/zhuyi/laiyuan）height=2，其余height=1；取值用 `"1.0", "end-1c"` 去掉末尾换行符
- **seed_data事务陷阱**：`seed_data()` 在异常时调用 `rollback()`，但SQLite默认auto-commit模式，未显式 `BEGIN`，回滚实际无效。如需原子性应先 `BEGIN`。

## Project Constraints

- 单人项目，原创作品
- 提交物：课程设计报告（含代码片段）+ 源码文件夹
- 评分：需求分析20% / 系统设计20% / 实现25% / 测试规范化15% / 报告质量15% / 考勤5%
