# PyCashier / adder - app to add product data to the data.json file
# Copyright (C) 2026 Irsyad Dzaky Nurghany
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys

# ── Helpers ───────────────────────────────────────────────────────────────────

def resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

def fmt_rp(amount):
    return f"Rp {int(amount):,}".replace(",", ".")

# ── Theme (same as cashier.py) ────────────────────────────────────────────────

BG       = "#0f1117"
SURFACE  = "#1a1d2e"
CARD     = "#252840"
CARD2    = "#2e3154"
ACCENT   = "#4f9eff"
ACCENT2  = "#3b82f6"
SUCCESS  = "#22c55e"
DANGER   = "#ef4444"
WARNING  = "#f59e0b"
TEXT     = "#f0f0f8"
SUBTEXT  = "#8080a8"
BORDER   = "#3d4068"

font_main = "Segoe UI"

HOVER    = "#353860"
SEL_BG   = "#1e3a5f"
SEL_FG   = "#7ec8ff"

FONT_TITLE  = (font_main, 15, "bold")
FONT_HEAD   = (font_main, 11, "bold")
FONT_BODY   = (font_main, 10)
FONT_SMALL  = (font_main, 9)

def apply_theme(root):
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".",
        background=BG, foreground=TEXT, fieldbackground=CARD,
        bordercolor=BORDER, font=FONT_BODY)
    style.configure("Modern.Treeview",
        background=CARD, foreground=TEXT,
        fieldbackground=CARD, rowheight=36,
        borderwidth=0, relief="flat", font=FONT_BODY)
    style.configure("Modern.Treeview.Heading",
        background=CARD2, foreground=SUBTEXT,
        borderwidth=0, relief="flat", padding=(8, 6),
        font=(font_main, 9, "bold"))
    style.map("Modern.Treeview",
        background=[("selected", SEL_BG)],
        foreground=[("selected", SEL_FG)])
    style.configure("Modern.Vertical.TScrollbar",
        background=CARD, troughcolor=SURFACE,
        borderwidth=0, arrowsize=14, relief="flat")
    style.map("Modern.Vertical.TScrollbar",
        background=[("active", ACCENT2)])


# ── Custom labeled entry widget ───────────────────────────────────────────────

class LabeledEntry(tk.Frame):
    def __init__(self, parent, label, placeholder="", **kwargs):
        super().__init__(parent, bg=CARD)
        self.placeholder = placeholder
        self._has_error = False

        tk.Label(self, text=label, font=(font_main, 8, "bold"),
                 bg=CARD, fg=SUBTEXT).pack(anchor="w")

        self.entry = tk.Entry(self, font=(font_main, 11), bg=CARD2, fg=TEXT,
                              insertbackground=TEXT, bd=0, relief="flat",
                              highlightthickness=2,
                              highlightbackground=BORDER,
                              highlightcolor=ACCENT, **kwargs)
        self.entry.pack(fill=tk.X, ipady=9, pady=(3, 0))

        self.hint = tk.Label(self, text="", font=(font_main, 8),
                             bg=CARD, fg=DANGER)
        self.hint.pack(anchor="w")

    def get(self):
        return self.entry.get()

    def set(self, val):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, str(val))

    def clear(self):
        self.entry.delete(0, tk.END)

    def focus(self):
        self.entry.focus_set()

    def bind(self, seq, func):
        self.entry.bind(seq, func)

    def error(self, msg=""):
        self._has_error = bool(msg)
        self.hint.config(text=msg)
        color = DANGER if msg else BORDER
        self.entry.config(highlightbackground=color)

    def ok(self):
        self.error("")


# ── Main App ──────────────────────────────────────────────────────────────────

class ProductAdderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PyCashier — Manajemen Produk")
        self.root.geometry("1000x680")
        self.root.minsize(860, 540)
        self.root.configure(bg=BG)

        apply_theme(root)

        self.data = []
        self.data_file = resource_path("data.json")

        if not self._load_data():
            messagebox.showerror("Error",
                f"Gagal memuat data.json di:\n{self.data_file}")
            root.destroy()
            return

        self._build_ui()
        self._refresh_table()

    def _load_data(self):
        if not os.path.exists(self.data_file):
            return False
        try:
            with open(self.data_file, "r", encoding='utf-8') as f:
                self.data = json.load(f)
            if not isinstance(self.data, list):
                raise ValueError("Format JSON harus berupa Array [ ]")
            return True
        except Exception:
            return False

    def _save_data(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan file: {e}")
            return False

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self.root, bg=SURFACE, height=60)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="📦  Manajemen Produk",
                 font=(font_main, 14, "bold"), bg=SURFACE, fg=TEXT).pack(
                     side=tk.LEFT, padx=20, pady=14)
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill=tk.X)

        # Body
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        # ── Left: Form ──
        left = tk.Frame(body, bg=BG, width=300)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        left.pack_propagate(False)

        form_card = tk.Frame(left, bg=CARD)
        form_card.pack(fill=tk.BOTH, expand=True)

        tk.Label(form_card, text="TAMBAH PRODUK BARU",
                 font=(font_main, 8, "bold"), bg=CARD, fg=SUBTEXT).pack(
                     anchor="w", padx=16, pady=(14, 2))
        tk.Frame(form_card, bg=BORDER, height=1).pack(fill=tk.X, padx=16, pady=(0, 14))

        fields_frame = tk.Frame(form_card, bg=CARD)
        fields_frame.pack(fill=tk.X, padx=16)

        self.f_id    = LabeledEntry(fields_frame, "ID PRODUK")
        self.f_id.pack(fill=tk.X, pady=(0, 10))

        self.f_name  = LabeledEntry(fields_frame, "NAMA PRODUK")
        self.f_name.pack(fill=tk.X, pady=(0, 10))

        self.f_price = LabeledEntry(fields_frame, "HARGA (Rp)")
        self.f_price.pack(fill=tk.X, pady=(0, 10))

        # Tab cycling
        self.f_id.bind("<Tab>",    lambda e: (self.f_name.focus(), "break"))
        self.f_name.bind("<Tab>",  lambda e: (self.f_price.focus(), "break"))
        self.f_price.bind("<Tab>", lambda e: (self.f_id.focus(),    "break"))

        # Enter to submit from last field
        self.f_id.bind("<Return>",    lambda e: self.f_name.focus())
        self.f_name.bind("<Return>",  lambda e: self.f_price.focus())
        self.f_price.bind("<Return>", lambda e: self._add_product())

        # Live validation clearing
        for f in [self.f_id, self.f_name, self.f_price]:
            f.entry.bind("<Key>", lambda e, fld=f: fld.ok())

        add_btn = tk.Button(form_card, text="＋  Tambah Produk",
                            font=(font_main, 11, "bold"),
                            bg=ACCENT2, fg="white",
                            bd=0, relief="flat", pady=12,
                            activebackground=ACCENT, activeforeground="white",
                            cursor="hand2", command=self._add_product)
        add_btn.pack(fill=tk.X, padx=16, pady=(10, 4))

        clear_btn = tk.Button(form_card, text="Bersihkan Form",
                              font=FONT_SMALL, bg=CARD2, fg=SUBTEXT,
                              bd=0, relief="flat", pady=8,
                              activebackground=HOVER,
                              cursor="hand2", command=self._clear_form)
        clear_btn.pack(fill=tk.X, padx=16, pady=(0, 16))

        # Status
        self.form_status = tk.Label(form_card, text="", font=FONT_SMALL,
                                    bg=CARD, fg=SUCCESS, wraplength=260)
        self.form_status.pack(padx=16, pady=(0, 12))

        # ── Right: Table ──
        right = tk.Frame(body, bg=BG)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tbl_header = tk.Frame(right, bg=CARD)
        tbl_header.pack(fill=tk.X, pady=(0, 8))
        tk.Label(tbl_header, text="DAFTAR PRODUK",
                 font=(font_main, 8, "bold"), bg=CARD, fg=SUBTEXT).pack(
                     side=tk.LEFT, padx=12, pady=10)
        self.count_lbl = tk.Label(tbl_header, text="",
                                   font=FONT_SMALL, bg=CARD, fg=SUBTEXT)
        self.count_lbl.pack(side=tk.RIGHT, padx=12)

        # Search filter
        search_row = tk.Frame(right, bg=BG)
        search_row.pack(fill=tk.X, pady=(0, 6))
        tk.Label(search_row, text="🔍", font=(font_main, 11),
                 bg=BG, fg=SUBTEXT).pack(side=tk.LEFT, padx=(0, 6))
        self.filter_var = tk.StringVar()
        self.filter_var.trace_add("write", lambda *_: self._refresh_table())
        filter_entry = tk.Entry(search_row, textvariable=self.filter_var,
                                font=FONT_BODY, bg=CARD2, fg=TEXT,
                                insertbackground=TEXT, bd=0, relief="flat",
                                highlightthickness=2,
                                highlightbackground=BORDER,
                                highlightcolor=ACCENT)
        filter_entry.pack(fill=tk.X, expand=True, ipady=7)

        # Table
        tbl_card = tk.Frame(right, bg=CARD)
        tbl_card.pack(fill=tk.BOTH, expand=True)

        sb = ttk.Scrollbar(tbl_card, style="Modern.Vertical.TScrollbar")
        sb.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 2))

        self.product_tree = ttk.Treeview(
            tbl_card, style="Modern.Treeview",
            columns=("id", "name", "price"), show="headings",
            yscrollcommand=sb.set)
        sb.config(command=self.product_tree.yview)

        self.product_tree.heading("id",    text="ID PRODUK")
        self.product_tree.heading("name",  text="NAMA PRODUK")
        self.product_tree.heading("price", text="HARGA")
        self.product_tree.column("id",    width=90,  anchor="center", stretch=False)
        self.product_tree.column("name",  width=300, anchor="w",      stretch=True)
        self.product_tree.column("price", width=150, anchor="e",      stretch=False)
        self.product_tree.pack(fill=tk.BOTH, expand=True, padx=(8, 0), pady=8)

        self.product_tree.bind("<Delete>",    self._delete_product)
        self.product_tree.bind("<BackSpace>", self._delete_product)
        self.product_tree.bind("<<TreeviewSelect>>", self._on_row_select)

        # Bottom bar
        tk.Frame(right, bg=BORDER, height=1).pack(fill=tk.X, pady=(4, 0))
        bot = tk.Frame(right, bg=BG, pady=6)
        bot.pack(fill=tk.X)

        del_btn = tk.Button(bot, text="🗑  Hapus Produk Dipilih",
                            font=FONT_SMALL, bg=CARD2, fg=SUBTEXT,
                            bd=0, relief="flat", padx=12, pady=7,
                            activebackground=DANGER, activeforeground="white",
                            cursor="hand2", command=self._delete_product)
        del_btn.pack(side=tk.LEFT)

        refresh_btn = tk.Button(bot, text="↺  Refresh",
                                font=FONT_SMALL, bg=CARD2, fg=SUBTEXT,
                                bd=0, relief="flat", padx=12, pady=7,
                                cursor="hand2", command=self._refresh_table)
        refresh_btn.pack(side=tk.LEFT, padx=(6, 0))

        # Status bar
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill=tk.X)
        self.status_bar = tk.Label(self.root,
                                    text="Siap  ·  Tab untuk pindah field, Enter untuk simpan",
                                    font=(font_main, 8), bg=SURFACE, fg=SUBTEXT,
                                    anchor="w", padx=14, pady=5)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.f_id.focus()

    # ── Logic ─────────────────────────────────────────────────────────────────

    def _validate_form(self):
        valid = True
        pid   = self.f_id.get().strip()
        name  = self.f_name.get().strip()
        price = self.f_price.get().strip().replace(".", "").replace(",", "")

        for f in [self.f_id, self.f_name, self.f_price]:
            f.ok()

        if not pid.isdigit():
            self.f_id.error("ID harus berupa angka")
            valid = False
        elif any(p.get('id') == int(pid) for p in self.data):
            self.f_id.error("ID sudah digunakan")
            valid = False

        if not name:
            self.f_name.error("Nama tidak boleh kosong")
            valid = False

        if not price.isdigit():
            self.f_price.error("Harga harus berupa angka")
            valid = False

        return valid

    def _add_product(self):
        if not self._validate_form():
            return
        new = {
            "id":    int(self.f_id.get().strip()),
            "name":  self.f_name.get().strip(),
            "price": int(self.f_price.get().strip().replace(".", "").replace(",", ""))
        }
        self.data.append(new)
        if self._save_data():
            self._refresh_table()
            self._clear_form()
            self.form_status.config(
                text=f"✓  '{new['name']}' berhasil ditambahkan!", fg=SUCCESS)
            self.status_bar.config(
                text=f"Produk '{new['name']}' disimpan  ·  Total: {len(self.data)} produk")
            self.root.after(4000, lambda: self.form_status.config(text=""))

    def _clear_form(self):
        for f in [self.f_id, self.f_name, self.f_price]:
            f.clear(); f.ok()
        self.f_id.focus()

    def _on_row_select(self, event=None):
        sel = self.product_tree.selection()
        if sel:
            vals = self.product_tree.item(sel[0], "values")
            self.status_bar.config(
                text=f"Dipilih: ID {vals[0]}  ·  {vals[1]}  ·  {vals[2]}  —  Delete untuk hapus")

    def _delete_product(self, event=None):
        sel = self.product_tree.selection()
        if not sel:
            return
        vals   = self.product_tree.item(sel[0], "values")
        p_id   = int(vals[0])
        p_name = vals[1]

        confirmed = messagebox.askyesno(
            "Konfirmasi Hapus",
            f"Hapus produk:\n\n  ID   : {p_id}\n  Nama : {p_name}\n\nTindakan ini tidak dapat dibatalkan.",
            icon="warning", parent=self.root)
        if not confirmed:
            return

        self.data = [p for p in self.data if p.get('id') != p_id]
        if self._save_data():
            self._refresh_table()
            self.status_bar.config(
                text=f"✓  '{p_name}' dihapus  ·  Total: {len(self.data)} produk")

    def _refresh_table(self, *_):
        q = self.filter_var.get().strip().lower() if hasattr(self, 'filter_var') else ""
        for row in self.product_tree.get_children():
            self.product_tree.delete(row)
        shown = 0
        for p in self.data:
            if q and q not in str(p.get('id', '')).lower() \
               and q not in p.get('name', '').lower():
                continue
            self.product_tree.insert("", tk.END, values=(
                p.get('id'), p.get('name'), fmt_rp(p.get('price', 0))))
            shown += 1
        total = len(self.data)
        self.count_lbl.config(
            text=f"{shown} / {total} produk" if q else f"{total} produk")


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app  = ProductAdderApp(root)
    root.mainloop()