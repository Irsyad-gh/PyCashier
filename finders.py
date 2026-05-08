# PyCashier / finders - app to find products by ID or name
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

# ── Theme ─────────────────────────────────────────────────────────────────────

BG      = "#0f1117"
SURFACE = "#1a1d2e"
CARD    = "#252840"
CARD2   = "#2e3154"
ACCENT  = "#4f9eff"
ACCENT2 = "#3b82f6"
TEXT    = "#f0f0f8"
SUBTEXT = "#8080a8"
BORDER  = "#3d4068"
HOVER   = "#353860"
SEL_BG  = "#1e3a5f"
SEL_FG  = "#7ec8ff"
SUCCESS = "#22c55e"

FONT_BODY  = (font_main, 10)
FONT_SMALL = (font_main, 9)

def apply_theme(root):
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".", background=BG, foreground=TEXT,
                    fieldbackground=CARD, font=FONT_BODY)
    style.configure("Modern.Treeview",
        background=CARD, foreground=TEXT, fieldbackground=CARD,
        rowheight=36, borderwidth=0, relief="flat", font=FONT_BODY)
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


# ── Main App ──────────────────────────────────────────────────────────────────

class ProductFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PyCashier — Pencarian Produk")
        self.root.geometry("860x600")
        self.root.minsize(640, 420)
        self.root.configure(bg=BG)

        apply_theme(root)

        self.data = []
        loaded = self._load_data()
        if not loaded:
            self.root.destroy()
            return
        self.data = loaded
        self._build_ui()
        self.perform_search()

    def _load_data(self):
        try:
            with open(resource_path("data.json"), "r", encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat data.json:\n{e}")
            return None

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self.root, bg=SURFACE, height=60)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="🔎  Pencarian Produk",
                 font=(font_main, 14, "bold"), bg=SURFACE, fg=TEXT).pack(
                     side=tk.LEFT, padx=20, pady=14)
        self.count_badge = tk.Label(hdr, text="", font=FONT_SMALL,
                                     bg=SURFACE, fg=SUBTEXT)
        self.count_badge.pack(side=tk.RIGHT, padx=20)
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill=tk.X)

        # Search
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        search_card = tk.Frame(body, bg=CARD)
        search_card.pack(fill=tk.X, pady=(0, 8))

        tk.Label(search_card, text="CARI BERDASARKAN ID ATAU NAMA",
                 font=(font_main, 8, "bold"), bg=CARD, fg=SUBTEXT).pack(
                     anchor="w", padx=12, pady=(10, 4))

        row = tk.Frame(search_card, bg=CARD)
        row.pack(fill=tk.X, padx=12, pady=(0, 8))

        tk.Label(row, text="🔍", font=(font_main, 12),
                 bg=CARD, fg=SUBTEXT).pack(side=tk.LEFT, padx=(0, 8))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.perform_search())
        self.search_entry = tk.Entry(row, textvariable=self.search_var,
                                     font=(font_main, 12), bg=CARD2, fg=TEXT,
                                     insertbackground=TEXT, bd=0, relief="flat",
                                     highlightthickness=2,
                                     highlightbackground=BORDER,
                                     highlightcolor=ACCENT)
        self.search_entry.pack(fill=tk.X, expand=True, ipady=9)
        self.search_entry.bind("<Escape>", lambda e: self.search_var.set(""))
        self.search_entry.bind("<Down>",   self._focus_table)
        self.search_entry.bind("<Return>", self._focus_table)

        hint = tk.Label(search_card,
                        text="Esc: bersihkan  ·  ↓ / Enter: ke daftar hasil",
                        font=(font_main, 8), bg=CARD, fg=SUBTEXT)
        hint.pack(anchor="w", padx=12, pady=(0, 8))

        # Table
        tbl_card = tk.Frame(body, bg=CARD)
        tbl_card.pack(fill=tk.BOTH, expand=True)

        sb = ttk.Scrollbar(tbl_card, style="Modern.Vertical.TScrollbar")
        sb.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 2))

        self.tree = ttk.Treeview(
            tbl_card, style="Modern.Treeview",
            columns=("id", "name", "price"), show="headings",
            yscrollcommand=sb.set)
        sb.config(command=self.tree.yview)

        self.tree.heading("id",    text="ID PRODUK")
        self.tree.heading("name",  text="NAMA PRODUK")
        self.tree.heading("price", text="HARGA")
        self.tree.column("id",    width=90,  anchor="center", stretch=False)
        self.tree.column("name",  width=480, anchor="w",      stretch=True)
        self.tree.column("price", width=150, anchor="e",      stretch=False)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=(8, 0), pady=8)

        self.tree.bind("<Escape>", lambda e: self.search_entry.focus())
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Detail strip
        self.detail_strip = tk.Label(tbl_card, text="",
                                      font=FONT_SMALL, bg=CARD2, fg=TEXT,
                                      anchor="w", padx=12, pady=7)
        self.detail_strip.pack(fill=tk.X)

        # Status bar
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill=tk.X)
        self.status_bar = tk.Label(self.root,
                                    text="Ketik untuk mencari produk",
                                    font=(font_main, 8), bg=SURFACE, fg=SUBTEXT,
                                    anchor="w", padx=14, pady=5)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.search_entry.focus_set()

    # ── Logic ─────────────────────────────────────────────────────────────────

    def perform_search(self, *_):
        q = self.search_var.get().strip().lower()
        for row in self.tree.get_children():
            self.tree.delete(row)
        results = [p for p in self.data
                   if not q
                   or q in str(p.get('id', '')).lower()
                   or q in p.get('name', '').lower()]
        for p in results:
            self.tree.insert("", tk.END, values=(
                p['id'], p['name'], fmt_rp(p['price'])))

        total = len(self.data)
        found = len(results)
        self.count_badge.config(text=f"{found} / {total} produk")
        self.status_bar.config(
            text=(f"{found} produk ditemukan untuk \"{self.search_var.get()}\""
                  if q else f"Menampilkan semua {total} produk"))

    def _focus_table(self, event=None):
        rows = self.tree.get_children()
        if rows:
            self.tree.selection_set(rows[0])
            self.tree.focus(rows[0])
            self.tree.focus_set()

    def _on_select(self, event=None):
        sel = self.tree.selection()
        if sel:
            vals = self.tree.item(sel[0], "values")
            self.detail_strip.config(
                text=f"  ID: {vals[0]}   ·   Nama: {vals[1]}   ·   Harga: {vals[2]}")


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app  = ProductFinderApp(root)
    root.mainloop()