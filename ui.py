"""
界面模块 — 使用Python内置tkinter构建桌面GUI。
包含6个功能标签页：药材管理、药材查询、配伍禁忌检查、禁忌规则管理、数据统计、数据操作。
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import DBManager


class TCMApp:
    """中医药药材查询与配伍禁忌系统主界面。"""

    def __init__(self, db: DBManager):
        self.db = db
        self.root = tk.Tk()
        self.root.title("中医药常用药材查询与配伍禁忌系统")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)

        style = ttk.Style()
        style.theme_use("clam")

        self._build_ui()

    def run(self):
        """启动主事件循环。"""
        self.root.mainloop()

    def _build_ui(self):
        """构建标签页界面。"""
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)

        self._build_herb_manage_tab(notebook)
        self._build_herb_search_tab(notebook)
        self._build_incompatibility_check_tab(notebook)
        self._build_rule_manage_tab(notebook)
        self._build_statistics_tab(notebook)
        self._build_data_ops_tab(notebook)

    # ======================== 1. 药材管理 ========================

    def _build_herb_manage_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="药材管理")

        paned = ttk.PanedWindow(frame, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=5, pady=5)

        # --- 左侧：药材列表 ---
        left = ttk.Frame(paned)
        paned.add(left, weight=1)

        ttk.Label(left, text="药材列表", font=("", 11, "bold")).pack(anchor="w")
        cols = ("ID", "名称", "拼音", "分类", "功效")
        self.herb_tree = ttk.Treeview(left, columns=cols, show="headings", height=18)
        for c in cols:
            self.herb_tree.heading(c, text=c)
        col_widths = [40, 100, 80, 80, 180]
        for c, w in zip(cols, col_widths):
            self.herb_tree.column(c, width=w)

        scrollbar = ttk.Scrollbar(left, orient="vertical", command=self.herb_tree.yview)
        self.herb_tree.configure(yscrollcommand=scrollbar.set)
        self.herb_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.herb_tree.bind("<<TreeviewSelect>>", self._on_herb_select)

        # --- 右侧：编辑表单 ---
        right = ttk.Frame(paned)
        paned.add(right, weight=1)

        ttk.Label(right, text="药材信息编辑", font=("", 11, "bold")).pack(anchor="w", pady=(0, 5))

        fields_frame = ttk.Frame(right)
        fields_frame.pack(fill="both", expand=True)

        self.herb_fields = {}
        labels = [
            ("name", "药材名称*"), ("pinyin", "拼音"), ("alias", "别名"),
            ("xingwei", "性味"), ("guijing", "归经"), ("gongxiao", "功效"),
            ("category", "功效分类"), ("yongfa_yongliang", "用法用量"),
            ("laiyuan", "来源"), ("zhuyi", "注意事项"),
        ]
        for i, (key, label) in enumerate(labels):
            ttk.Label(fields_frame, text=f"{label}：").grid(
                row=i, column=0, sticky="e", padx=5, pady=2
            )
            w = tk.Text(fields_frame, height=1 if key not in ("gongxiao", "zhuyi", "laiyuan") else 2,
                        width=30)
            w.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
            self.herb_fields[key] = w
        fields_frame.columnconfigure(1, weight=1)

        # 按钮
        btn_frame = ttk.Frame(right)
        btn_frame.pack(fill="x", pady=5)
        self._herb_add_btn = ttk.Button(btn_frame, text="新增药材", command=self._add_herb)
        self._herb_add_btn.pack(side="left", padx=3)
        ttk.Button(btn_frame, text="更新所选", command=self._update_herb).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="删除所选", command=self._delete_herb).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="清空表单", command=self._clear_herb_form).pack(side="left", padx=3)

        self._refresh_herb_list()

    def _refresh_herb_list(self):
        """刷新药材列表。"""
        for item in self.herb_tree.get_children():
            self.herb_tree.delete(item)
        for herb in self.db.get_all_herbs():
            self.herb_tree.insert("", "end", values=(
                herb["id"], herb["name"], herb["pinyin"],
                herb["category"], herb["gongxiao"]
            ))

    def _on_herb_select(self, event):
        """选中列表中的药材时，填充表单。"""
        sel = self.herb_tree.selection()
        if not sel:
            return
        values = self.herb_tree.item(sel[0], "values")
        herb_id = values[0]
        herb = self.db.get_herb(herb_id)
        if not herb:
            return
        self._clear_herb_form()
        for key, widget in self.herb_fields.items():
            widget.insert("1.0", herb.get(key, ""))

    def _clear_herb_form(self):
        """清空表单。"""
        for widget in self.herb_fields.values():
            widget.delete("1.0", "end")

    def _get_form_data(self) -> dict:
        """从表单收集数据。"""
        return {key: w.get("1.0", "end-1c").strip() for key, w in self.herb_fields.items()}

    def _add_herb(self):
        """新增药材。"""
        data = self._get_form_data()
        if not data["name"]:
            messagebox.showwarning("提示", "药材名称为必填项。")
            return
        hid = self.db.add_herb(data)
        if hid == -1:
            messagebox.showerror("错误", "药材名称已存在，请勿重复添加。")
        else:
            messagebox.showinfo("成功", f"药材「{data['name']}」已添加。")
            self._clear_herb_form()
            self._refresh_herb_list()

    def _update_herb(self):
        """更新所选药材。"""
        sel = self.herb_tree.selection()
        if not sel:
            messagebox.showwarning("提示", "请先在左侧列表中选择要更新的药材。")
            return
        herb_id = self.herb_tree.item(sel[0], "values")[0]
        data = self._get_form_data()
        if not data["name"]:
            messagebox.showwarning("提示", "药材名称为必填项。")
            return
        if self.db.update_herb(herb_id, data):
            messagebox.showinfo("成功", "药材信息已更新。")
            self._refresh_herb_list()
        else:
            messagebox.showerror("错误", "更新失败，可能名称重复。")

    def _delete_herb(self):
        """删除所选药材。"""
        sel = self.herb_tree.selection()
        if not sel:
            messagebox.showwarning("提示", "请先在左侧列表中选择要删除的药材。")
            return
        herb_name = self.herb_tree.item(sel[0], "values")[1]
        if not messagebox.askyesno("确认", f"确定要删除药材「{herb_name}」吗？此操作不可恢复。"):
            return
        herb_id = self.herb_tree.item(sel[0], "values")[0]
        self.db.delete_herb(herb_id)
        messagebox.showinfo("成功", f"药材「{herb_name}」已删除。")
        self._clear_herb_form()
        self._refresh_herb_list()

    # ======================== 2. 药材查询 ========================

    def _build_herb_search_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="药材查询")

        # 搜索栏
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill="x", padx=5, pady=5)
        ttk.Label(search_frame, text="关键词：").pack(side="left")
        self.search_entry = ttk.Entry(search_frame, width=25)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda e: self._search_herbs())

        ttk.Label(search_frame, text="搜索范围：").pack(side="left", padx=(10, 0))
        self.search_field = ttk.Combobox(
            search_frame, values=["name", "pinyin", "category", "gongxiao", "alias"],
            state="readonly", width=10
        )
        self.search_field.set("name")
        self.search_field.pack(side="left", padx=5)

        ttk.Button(search_frame, text="查询", command=self._search_herbs).pack(side="left", padx=5)
        ttk.Button(search_frame, text="显示全部", command=self._refresh_herb_list
                   ).pack(side="left", padx=5)

        # 结果列表
        cols = ("ID", "名称", "拼音", "分类", "功效", "性味", "归经")
        self.search_tree = ttk.Treeview(frame, columns=cols, show="headings", height=20)
        for c in cols:
            self.search_tree.heading(c, text=c)
        widths = [40, 100, 80, 80, 180, 100, 100]
        for c, w in zip(cols, widths):
            self.search_tree.column(c, width=w)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.search_tree.yview)
        self.search_tree.configure(yscrollcommand=scrollbar.set)
        self.search_tree.pack(side="left", fill="both", expand=True, padx=5)
        scrollbar.pack(side="right", fill="y")

        # 详情面板
        self.search_detail = tk.Text(frame, height=6, state="disabled", wrap="word")
        self.search_detail.pack(fill="x", padx=5, pady=5)

        self.search_tree.bind("<<TreeviewSelect>>", self._on_search_select)

    def _search_herbs(self):
        """执行查询。"""
        keyword = self.search_entry.get().strip()
        field = self.search_field.get()
        if not keyword:
            return
        results = self.db.search_herbs(keyword, field)
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        for h in results:
            self.search_tree.insert("", "end", values=(
                h["id"], h["name"], h["pinyin"], h["category"],
                h["gongxiao"], h.get("xingwei", ""), h.get("guijing", "")
            ))

    def _on_search_select(self, event):
        """选中搜索结果时显示详情。"""
        sel = self.search_tree.selection()
        if not sel:
            return
        herb_id = self.search_tree.item(sel[0], "values")[0]
        herb = self.db.get_herb(herb_id)
        if not herb:
            return
        self.search_detail.configure(state="normal")
        self.search_detail.delete("1.0", "end")
        info = (
            f"【药材名称】{herb['name']}\n"
            f"【拼音】{herb['pinyin']}    【别名】{herb['alias']}\n"
            f"【性味】{herb['xingwei']}    【归经】{herb['guijing']}\n"
            f"【功效】{herb['gongxiao']}\n"
            f"【功效分类】{herb['category']}\n"
            f"【用法用量】{herb['yongfa_yongliang']}\n"
            f"【来源】{herb['laiyuan']}\n"
            f"【注意事项】{herb['zhuyi']}\n"
        )
        self.search_detail.insert("1.0", info)
        self.search_detail.configure(state="disabled")

    # ======================== 3. 配伍禁忌检查 ========================

    def _build_incompatibility_check_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="配伍禁忌检查")

        top = ttk.Frame(frame)
        top.pack(fill="both", expand=True, padx=5, pady=5)

        # 已选药材列表
        left = ttk.Frame(top)
        left.pack(side="left", fill="both", expand=True)
        ttk.Label(left, text="待检查的药材组合：", font=("", 10, "bold")).pack(anchor="w")

        btn_row = ttk.Frame(left)
        btn_row.pack(fill="x", pady=3)
        ttk.Button(btn_row, text="添加所选药材", command=self._add_to_check).pack(side="left", padx=2)
        ttk.Button(btn_row, text="移除所选", command=self._remove_from_check).pack(side="left", padx=2)
        ttk.Button(btn_row, text="清空列表", command=self._clear_check_list).pack(side="left", padx=2)

        self.check_listbox = tk.Listbox(left, height=12, selectmode="extended")
        self.check_listbox.pack(fill="both", expand=True)

        # 检查按钮
        ttk.Button(left, text="执行配伍禁忌检查", command=self._do_incompatibility_check
                   ).pack(fill="x", pady=5)

        # 可选药材
        right = ttk.Frame(top)
        right.pack(side="right", fill="both", expand=True)
        ttk.Label(right, text="可选药材（双击添加）：", font=("", 10, "bold")).pack(anchor="w")
        self.available_listbox = tk.Listbox(right, height=12, selectmode="extended")
        self.available_listbox.pack(fill="both", expand=True)
        self.available_listbox.bind("<Double-1>", lambda e: self._add_to_check())

        # 结果区域
        result_frame = ttk.Frame(frame)
        result_frame.pack(fill="both", expand=True, padx=5, pady=5)
        ttk.Label(result_frame, text="检查结果：", font=("", 10, "bold")).pack(anchor="w")
        self.check_result = tk.Text(result_frame, height=10, state="disabled", wrap="word")
        self.check_result.pack(fill="both", expand=True)

        self._refresh_available_list()

    def _refresh_available_list(self):
        """刷新可选药材列表。"""
        self.available_listbox.delete(0, "end")
        for herb in self.db.get_all_herbs():
            self.available_listbox.insert("end", herb["name"])

    def _add_to_check(self):
        """将选中药材加入待检查列表。"""
        sel = self.available_listbox.curselection()
        names = [self.available_listbox.get(i) for i in sel]
        for name in names:
            existing = self.check_listbox.get(0, "end")
            if name not in existing:
                self.check_listbox.insert("end", name)

    def _remove_from_check(self):
        """从待检查列表移除选中。"""
        sel = list(self.check_listbox.curselection())
        for i in reversed(sel):
            self.check_listbox.delete(i)

    def _clear_check_list(self):
        """清空待检查列表。"""
        self.check_listbox.delete(0, "end")

    def _do_incompatibility_check(self):
        """执行配伍禁忌检查。"""
        herb_names = list(self.check_listbox.get(0, "end"))
        if len(herb_names) < 2:
            messagebox.showwarning("提示", "请至少选择两味药材进行检查。")
            return

        conflicts = self.db.check_incompatibility(herb_names)
        self.check_result.configure(state="normal")
        self.check_result.delete("1.0", "end")

        if not conflicts:
            self.check_result.insert("1.0",
                f"检查结果：未发现配伍禁忌。\n\n"
                f"已检查药材组合（共{len(herb_names)}味）：{'、'.join(herb_names)}\n"
            )
        else:
            lines = [f"⚠ 发现 {len(conflicts)} 处配伍禁忌：\n"]
            for c in conflicts:
                lines.append(
                    f"  ✘ {c['herb_1']} + {c['herb_2']}"
                    f"  [{c['rule_type']}] {c['description']}\n"
                )
            lines.append(f"\n已检查药材：{'、'.join(herb_names)}\n")
            self.check_result.insert("1.0", "".join(lines))

        self.check_result.configure(state="disabled")

    # ======================== 4. 禁忌规则管理 ========================

    def _build_rule_manage_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="禁忌规则管理")

        paned = ttk.PanedWindow(frame, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=5, pady=5)

        # 左侧：规则列表
        left = ttk.Frame(paned)
        paned.add(left, weight=1)
        ttk.Label(left, text="配伍禁忌规则列表", font=("", 11, "bold")).pack(anchor="w")
        cols = ("ID", "药材A", "药材B", "类型", "说明")
        self.rule_tree = ttk.Treeview(left, columns=cols, show="headings", height=18)
        for c in cols:
            self.rule_tree.heading(c, text=c)
        widths = [40, 100, 100, 80, 200]
        for c, w in zip(cols, widths):
            self.rule_tree.column(c, width=w)

        scrollbar = ttk.Scrollbar(left, orient="vertical", command=self.rule_tree.yview)
        self.rule_tree.configure(yscrollcommand=scrollbar.set)
        self.rule_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.rule_tree.bind("<<TreeviewSelect>>", self._on_rule_select)

        # 右侧：规则编辑
        right = ttk.Frame(paned)
        paned.add(right, weight=1)
        ttk.Label(right, text="禁忌规则编辑", font=("", 11, "bold")).pack(anchor="w", pady=(0, 5))

        form = ttk.Frame(right)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text="药材A：").grid(row=0, column=0, sticky="e", padx=5, pady=3)
        self.rule_herb_a = ttk.Combobox(form, values=[], width=22)
        self.rule_herb_a.grid(row=0, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(form, text="药材B：").grid(row=1, column=0, sticky="e", padx=5, pady=3)
        self.rule_herb_b = ttk.Combobox(form, values=[], width=22)
        self.rule_herb_b.grid(row=1, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(form, text="禁忌类型：").grid(row=2, column=0, sticky="e", padx=5, pady=3)
        self.rule_type = ttk.Combobox(form, values=["十八反", "十九畏", "其它"], width=22)
        self.rule_type.grid(row=2, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(form, text="说明：").grid(row=3, column=0, sticky="ne", padx=5, pady=3)
        self.rule_desc = tk.Text(form, height=3, width=28)
        self.rule_desc.grid(row=3, column=1, sticky="w", padx=5, pady=3)

        btn_frame = ttk.Frame(right)
        btn_frame.pack(fill="x", pady=5)
        ttk.Button(btn_frame, text="新增规则", command=self._add_rule).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="更新规则", command=self._update_rule).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="删除规则", command=self._delete_rule).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="清空表单", command=self._clear_rule_form).pack(side="left", padx=3)

        self._refresh_rule_list()
        self._refresh_rule_combos()

    def _refresh_rule_list(self):
        for item in self.rule_tree.get_children():
            self.rule_tree.delete(item)
        for r in self.db.get_all_rules():
            self.rule_tree.insert("", "end", values=(
                r["id"], r["herb_a"], r["herb_b"], r["rule_type"], r["description"]
            ))

    def _refresh_rule_combos(self):
        names = [h["name"] for h in self.db.get_all_herbs()]
        self.rule_herb_a["values"] = names
        self.rule_herb_b["values"] = names

    def _on_rule_select(self, event):
        sel = self.rule_tree.selection()
        if not sel:
            return
        values = self.rule_tree.item(sel[0], "values")
        self.rule_herb_a.set(values[1])
        self.rule_herb_b.set(values[2])
        self.rule_type.set(values[3])
        self.rule_desc.delete("1.0", "end")
        self.rule_desc.insert("1.0", values[4])

    def _clear_rule_form(self):
        self.rule_herb_a.set("")
        self.rule_herb_b.set("")
        self.rule_type.set("")
        self.rule_desc.delete("1.0", "end")

    def _add_rule(self):
        a = self.rule_herb_a.get().strip()
        b = self.rule_herb_b.get().strip()
        rt = self.rule_type.get().strip()
        desc = self.rule_desc.get("1.0", "end-1c").strip()
        if not a or not b:
            messagebox.showwarning("提示", "药材A和药材B为必填项。")
            return
        if a == b:
            messagebox.showwarning("提示", "药材A和药材B不能相同。")
            return
        rid = self.db.add_rule(a, b, rt, desc)
        if rid == -1:
            messagebox.showerror("错误", "该禁忌规则已存在。")
        else:
            messagebox.showinfo("成功", f"禁忌规则「{a}+{b}」已添加。")
            self._clear_rule_form()
            self._refresh_rule_list()

    def _update_rule(self):
        sel = self.rule_tree.selection()
        if not sel:
            messagebox.showwarning("提示", "请先选择要更新的规则。")
            return
        rule_id = self.rule_tree.item(sel[0], "values")[0]
        a = self.rule_herb_a.get().strip()
        b = self.rule_herb_b.get().strip()
        rt = self.rule_type.get().strip()
        desc = self.rule_desc.get("1.0", "end-1c").strip()
        if not a or not b:
            messagebox.showwarning("提示", "药材A和药材B为必填项。")
            return
        if a == b:
            messagebox.showwarning("提示", "药材A和药材B不能相同。")
            return
        if self.db.update_rule(rule_id, a, b, rt, desc):
            messagebox.showinfo("成功", "规则已更新。")
            self._refresh_rule_list()
        else:
            messagebox.showerror("错误", "更新失败。")

    def _delete_rule(self):
        sel = self.rule_tree.selection()
        if not sel:
            messagebox.showwarning("提示", "请先选择要删除的规则。")
            return
        values = self.rule_tree.item(sel[0], "values")
        if not messagebox.askyesno("确认",
            f"确定要删除「{values[1]}+{values[2]}」的禁忌规则吗？"):
            return
        self.db.delete_rule(values[0])
        messagebox.showinfo("成功", "规则已删除。")
        self._clear_rule_form()
        self._refresh_rule_list()

    # ======================== 5. 数据统计 ========================

    def _build_statistics_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="数据统计")

        self.stats_text = tk.Text(frame, state="disabled", wrap="word",
                                   font=("Consolas", 11))
        self.stats_text.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Button(frame, text="刷新统计", command=self._refresh_stats).pack(pady=5)

    def _refresh_stats(self):
        """刷新统计数据。"""
        stats = self.db.get_statistics()
        self.stats_text.configure(state="normal")
        self.stats_text.delete("1.0", "end")

        lines = [
            "═" * 40 + "\n",
            "    中医药常用药材查询与配伍禁忌系统\n",
            "    数 据 统 计\n",
            "═" * 40 + "\n\n",
            f"  药材总数：{stats['herb_count']} 种\n",
            f"  配伍禁忌规则总数：{stats['rule_count']} 组\n\n",
            "─" * 40 + "\n",
            "  功效分类统计：\n",
        ]
        for cat, cnt in stats["categories"]:
            lines.append(f"    · {cat}：{cnt} 种\n")

        lines.append("\n─" * 40 + "\n")
        lines.append("  禁忌类型统计：\n")
        for rt, cnt in stats["rule_types"]:
            lines.append(f"    · {rt}：{cnt} 组\n")

        lines.append("\n" + "═" * 40 + "\n")
        self.stats_text.insert("1.0", "".join(lines))
        self.stats_text.configure(state="disabled")

    # ======================== 6. 数据操作 ========================

    def _build_data_ops_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="数据操作")

        ttk.Label(frame, text="数据导入 / 导出 / 重置",
                  font=("", 12, "bold")).pack(pady=15)

        ttk.Button(frame, text="导出数据到 JSON 文件",
                   command=self._export_data, width=30).pack(pady=8)
        ttk.Button(frame, text="从 JSON 文件导入数据",
                   command=self._import_data, width=30).pack(pady=8)
        ttk.Separator(frame, orient="horizontal").pack(fill="x", padx=40, pady=15)
        ttk.Button(frame, text="⚠ 清空/重置数据库（所有数据将丢失）",
                   command=self._reset_database, width=35).pack(pady=8)

        self.ops_status = ttk.Label(frame, text="", foreground="gray")
        self.ops_status.pack(pady=10)

    def _export_data(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile="tcm_data.json",
            title="导出数据"
        )
        if not filepath:
            return
        try:
            count = self.db.export_to_json(filepath)
            self.ops_status.configure(
                text=f"成功导出 {count} 条记录到：{filepath}"
            )
            messagebox.showinfo("导出成功", f"已导出 {count} 条记录。")
        except Exception as e:
            messagebox.showerror("导出失败", str(e))

    def _import_data(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            title="导入数据"
        )
        if not filepath:
            return
        try:
            herbs, rules = self.db.import_from_json(filepath)
            self.ops_status.configure(
                text=f"导入完成：{herbs} 条药材，{rules} 条规则"
            )
            messagebox.showinfo("导入成功",
                f"已导入 {herbs} 条药材记录和 {rules} 条禁忌规则。")
            self._refresh_herb_list()
            self._refresh_rule_list()
            self._refresh_available_list()
            self._refresh_rule_combos()
        except Exception as e:
            messagebox.showerror("导入失败", f"文件格式错误：{e}")

    def _reset_database(self):
        if not messagebox.askyesno("⚠ 确认重置",
            "此操作将删除数据库中所有数据（药材和禁忌规则）。\n\n"
            "重置后系统将自动重新载入内置测试数据。\n\n"
            "确定要继续吗？"):
            return

        self.db.reset_database()
        from data import SEED_HERBS, SEED_RULES
        self.db.seed_data(SEED_HERBS, SEED_RULES)
        self._refresh_herb_list()
        self._refresh_rule_list()
        self._refresh_available_list()
        self._refresh_rule_combos()
        self._refresh_stats()
        self.ops_status.configure(text="数据库已重置并重新载入测试数据。")
        messagebox.showinfo("完成", "数据库已重置，测试数据已重新载入。")
