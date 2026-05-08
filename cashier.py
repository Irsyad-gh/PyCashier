# PyCashier / cashier - app to find products by ID and add up the total price
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
from datetime import datetime

# ── Helpers ──────────────────────────────────────────────────────────────────

def resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

def fmt_rp(amount):
    return f"Rp {int(amount):,}".replace(",", ".")

# ── Theme ─────────────────────────────────────────────────────────────────────

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
HOVER    = "#353860"
SEL_BG   = "#1e3a5f"
SEL_FG   = "#7ec8ff"

import platform
current_os = platform.system()

if current_os == "Windows":
    font_main = "Segoe UI"
    font_mono = "Consolas"
elif current_os == "Darwin": # macOS
    font_main = "Helvetica"
    font_mono = "Menlo"
else: # Linux/Ubuntu
    font_main = "Ubuntu"
    font_mono = "DejaVu Sans Mono"

FONT_TITLE = (font_main, 15, "bold")
FONT_HEAD  = (font_main, 11, "bold")
FONT_BODY  = (font_main, 10)
FONT_SMALL = (font_main, 9)
FONT_MONO  = (font_mono, 10)
FONT_TOTAL = (font_main, 18, "bold")
def apply_theme(root):
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".",
        background=BG, foreground=TEXT, fieldbackground=CARD,
        bordercolor=BORDER, troughcolor=SURFACE,
        selectbackground=SEL_BG, selectforeground=SEL_FG,
        font=FONT_BODY)

    # Entry
    style.configure("Modern.TEntry",
        fieldbackground=CARD, foreground=TEXT, insertcolor=TEXT,
        bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER,
        padding=(10, 8))
    style.map("Modern.TEntry",
        bordercolor=[("focus", ACCENT)],
        lightcolor=[("focus", ACCENT)],
        darkcolor=[("focus", ACCENT)])

    # Buttons
    style.configure("Accent.TButton",
        background=ACCENT2, foreground="white",
        borderwidth=0, padding=(14, 9), font=FONT_HEAD,
        relief="flat")
    style.map("Accent.TButton",
        background=[("active", ACCENT), ("pressed", "#2563eb")])

    style.configure("Danger.TButton",
        background=DANGER, foreground="white",
        borderwidth=0, padding=(10, 7), font=FONT_BODY,
        relief="flat")
    style.map("Danger.TButton",
        background=[("active", "#dc2626"), ("pressed", "#b91c1c")])

    style.configure("Ghost.TButton",
        background=CARD2, foreground=TEXT,
        borderwidth=0, padding=(10, 7), font=FONT_BODY,
        relief="flat")
    style.map("Ghost.TButton",
        background=[("active", HOVER)])

    # Treeview
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
    style.map("Modern.Treeview.Heading",
        background=[("active", HOVER)])

    # Scrollbar
    style.configure("Modern.Vertical.TScrollbar",
        background=CARD, troughcolor=SURFACE,
        borderwidth=0, arrowsize=14, relief="flat")
    style.map("Modern.Vertical.TScrollbar",
        background=[("active", ACCENT2)])

    # Frame/Label
    style.configure("Card.TFrame", background=CARD, relief="flat")
    style.configure("Surface.TFrame", background=SURFACE, relief="flat")
    style.configure("BG.TFrame", background=BG, relief="flat")

    style.configure("Card.TLabel", background=CARD, foreground=TEXT)
    style.configure("Surface.TLabel", background=SURFACE, foreground=TEXT)
    style.configure("Sub.TLabel", background=SURFACE, foreground=SUBTEXT, font=FONT_SMALL)
    style.configure("BG.TLabel", background=BG, foreground=TEXT)

    # Separator
    style.configure("TSeparator", background=BORDER)

# ── Checkout Recap Dialog ─────────────────────────────────────────────────────

class CheckoutDialog(tk.Toplevel):
    def __init__(self, parent, cart_items, on_confirm, on_back):
        super().__init__(parent)
        self.on_confirm = on_confirm
        self.on_back = on_back
        self.cart_items = cart_items  # list of (product_dict, qty)

        self.title("Konfirmasi Pembayaran")
        self.configure(bg=SURFACE)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build()
        self._center(parent)
        self.protocol("WM_DELETE_WINDOW", self._back)
        self.bind("<Escape>", lambda e: self._back())
        self.bind("<Return>", lambda e: self._confirm())

    def _center(self, parent):
        self.update_idletasks()
        pw = parent.winfo_x(); ph = parent.winfo_y()
        pw2 = parent.winfo_width(); ph2 = parent.winfo_height()
        w = self.winfo_width(); h = self.winfo_height()
        x = pw + (pw2 - w) // 2
        y = ph + (ph2 - h) // 2
        self.geometry(f"+{x}+{y}")

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=ACCENT2, pady=16)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="✓  Rekapan Transaksi", font=FONT_TITLE,
                 bg=ACCENT2, fg="white").pack()
        tk.Label(hdr, text=datetime.now().strftime("%d %B %Y  %H:%M"),
                 font=FONT_SMALL, bg=ACCENT2, fg="#c0d8ff").pack()

        # Body
        body = tk.Frame(self, bg=SURFACE, padx=24, pady=16)
        body.pack(fill=tk.BOTH)

        # Item table header
        th = tk.Frame(body, bg=CARD2)
        th.pack(fill=tk.X, pady=(0, 1))
        for txt, w, anchor in [("Produk", 26, "w"), ("Qty", 5, "center"),
                                 ("Harga", 12, "e"), ("Subtotal", 14, "e")]:
            tk.Label(th, text=txt, font=(font_main, 9, "bold"),
                     bg=CARD2, fg=SUBTEXT, width=w, anchor=anchor,
                     padx=8, pady=6).pack(side=tk.LEFT)

        # Items
        scroll_frame = tk.Frame(body, bg=SURFACE)
        scroll_frame.pack(fill=tk.X)

        total = 0
        for i, (prod, qty) in enumerate(self.cart_items):
            sub = prod['price'] * qty
            total += sub
            row_bg = CARD if i % 2 == 0 else CARD2
            row = tk.Frame(scroll_frame, bg=row_bg)
            row.pack(fill=tk.X, pady=0)
            for txt, w, anchor in [
                (prod['name'], 26, "w"),
                (str(qty), 5, "center"),
                (fmt_rp(prod['price']), 12, "e"),
                (fmt_rp(sub), 14, "e")
            ]:
                tk.Label(row, text=txt, font=FONT_BODY, bg=row_bg, fg=TEXT,
                         width=w, anchor=anchor, padx=8, pady=8).pack(side=tk.LEFT)

        # Divider
        tk.Frame(body, bg=BORDER, height=1).pack(fill=tk.X, pady=(10, 0))

        # Total row
        tot_row = tk.Frame(body, bg=SURFACE, pady=6)
        tot_row.pack(fill=tk.X)
        tk.Label(tot_row, text="TOTAL", font=(font_main, 11, "bold"),
                 bg=SURFACE, fg=SUBTEXT).pack(side=tk.LEFT)
        self.total_val = total
        tk.Label(tot_row, text=fmt_rp(total), font=(font_main, 14, "bold"),
                 bg=SURFACE, fg=SUCCESS).pack(side=tk.RIGHT)

        # Cash input
        cash_row = tk.Frame(body, bg=SURFACE, pady=4)
        cash_row.pack(fill=tk.X)
        tk.Label(cash_row, text="Uang Diterima (Rp):", font=FONT_BODY,
                 bg=SURFACE, fg=TEXT).pack(side=tk.LEFT)

        self.cash_var = tk.StringVar()
        self.cash_var.trace_add("write", self._update_change)
        cash_entry = tk.Entry(cash_row, textvariable=self.cash_var,
                              font=FONT_MONO, bg=CARD, fg=TEXT,
                              insertbackground=TEXT, bd=0,
                              relief="flat", width=16,
                              highlightthickness=2,
                              highlightbackground=BORDER,
                              highlightcolor=ACCENT)
        cash_entry.pack(side=tk.RIGHT, padx=(8, 0), ipady=6)
        cash_entry.focus_set()

        # Change row
        chg_row = tk.Frame(body, bg=SURFACE, pady=4)
        chg_row.pack(fill=tk.X)
        tk.Label(chg_row, text="Kembalian:", font=FONT_BODY,
                 bg=SURFACE, fg=TEXT).pack(side=tk.LEFT)
        self.change_label = tk.Label(chg_row, text="—", font=(font_main, 11, "bold"),
                                     bg=SURFACE, fg=WARNING)
        self.change_label.pack(side=tk.RIGHT)

        # Buttons
        tk.Frame(body, bg=BORDER, height=1).pack(fill=tk.X, pady=(12, 8))
        btn_row = tk.Frame(body, bg=SURFACE)
        btn_row.pack(fill=tk.X)

        back_btn = tk.Button(btn_row, text="← Kembali",
                             font=FONT_BODY, bg=CARD2, fg=TEXT,
                             bd=0, relief="flat", padx=18, pady=10,
                             activebackground=HOVER, activeforeground=TEXT,
                             cursor="hand2", command=self._back)
        back_btn.pack(side=tk.LEFT)

        ok_btn = tk.Button(btn_row, text="✓  Selesai & Transaksi Baru",
                           font=FONT_HEAD, bg=SUCCESS, fg="white",
                           bd=0, relief="flat", padx=18, pady=10,
                           activebackground="#16a34a", activeforeground="white",
                           cursor="hand2", command=self._confirm)
        ok_btn.pack(side=tk.RIGHT)

    def _update_change(self, *_):
        raw = self.cash_var.get().replace(".", "").replace(",", "")
        try:
            cash = int(raw)
            change = cash - self.total_val
            if change >= 0:
                self.change_label.config(text=fmt_rp(change), fg=SUCCESS)
            else:
                self.change_label.config(text=f"Kurang {fmt_rp(-change)}", fg=DANGER)
        except ValueError:
            self.change_label.config(text="—", fg=WARNING)

    def _back(self):
        self.destroy()
        self.on_back()

    def _confirm(self):
        self.destroy()
        self.on_confirm()


# ── Main App ──────────────────────────────────────────────────────────────────

class CashierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PyCashier — Kasir")
        self.root.geometry("1100x700")
        self.root.minsize(900, 580)
        self.root.configure(bg=BG)

        apply_theme(root)

        self.data = []
        self.cart = {}   # id -> {"product": ..., "qty": int}
        self._dialog_open = False

        loaded = self._load_data()
        if loaded is None:
            self.root.after(100, self.root.destroy)
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

    # ── UI Construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Header ──
        hdr = tk.Frame(self.root, bg=SURFACE, height=60)
        hdr.pack(fill=tk.X, side=tk.TOP)
        hdr.pack_propagate(False)

        tk.Label(hdr, text="🛒  PyCashier", font=(font_main, 14, "bold"),
                 bg=SURFACE, fg=TEXT).pack(side=tk.LEFT, padx=20, pady=14)

        self.clock_label = tk.Label(hdr, text="", font=FONT_SMALL,
                                    bg=SURFACE, fg=SUBTEXT)
        self.clock_label.pack(side=tk.RIGHT, padx=20)
        self._update_clock()

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill=tk.X)

        # ── Main body ──
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        # ── Left panel: Search + Results ──
        left = tk.Frame(body, bg=BG)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Search bar
        search_card = tk.Frame(left, bg=CARD, bd=0)
        search_card.pack(fill=tk.X, pady=(0, 8))

        tk.Label(search_card, text="CARI PRODUK", font=(font_main, 8, "bold"),
                 bg=CARD, fg=SUBTEXT).pack(anchor="w", padx=12, pady=(10, 2))

        search_inner = tk.Frame(search_card, bg=CARD)
        search_inner.pack(fill=tk.X, padx=12, pady=(0, 10))

        tk.Label(search_inner, text="🔍", font=(font_main, 12),
                 bg=CARD, fg=SUBTEXT).pack(side=tk.LEFT, padx=(0, 6))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.perform_search())
        self.search_entry = tk.Entry(search_inner, textvariable=self.search_var,
                                     font=(font_main, 12), bg=CARD2, fg=TEXT,
                                     insertbackground=TEXT, bd=0, relief="flat",
                                     highlightthickness=2,
                                     highlightbackground=BORDER,
                                     highlightcolor=ACCENT)
        self.search_entry.pack(fill=tk.X, expand=True, ipady=8)
        self.search_entry.bind("<Return>",   self._search_enter)
        self.search_entry.bind("<Down>",     self._focus_results)
        self.search_entry.bind("<Escape>",   self._clear_search)

        hint = tk.Label(search_card,
                        text="Enter: tambah ke keranjang  ·  ↓: pilih dari daftar  ·  Esc: bersihkan",
                        font=(font_main, 8), bg=CARD, fg=SUBTEXT)
        hint.pack(anchor="w", padx=12, pady=(0, 8))

        # Results table
        res_card = tk.Frame(left, bg=CARD)
        res_card.pack(fill=tk.BOTH, expand=True, pady=(0, 0))

        tk.Label(res_card, text="HASIL PENCARIAN", font=(font_main, 8, "bold"),
                 bg=CARD, fg=SUBTEXT).pack(anchor="w", padx=12, pady=(10, 4))

        tree_frame = tk.Frame(res_card, bg=CARD)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        sb = ttk.Scrollbar(tree_frame, style="Modern.Vertical.TScrollbar")
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self.search_tree = ttk.Treeview(
            tree_frame, style="Modern.Treeview",
            columns=("id", "name", "price"), show="headings",
            yscrollcommand=sb.set, selectmode="browse")
        sb.config(command=self.search_tree.yview)

        self.search_tree.heading("id",    text="ID")
        self.search_tree.heading("name",  text="NAMA PRODUK")
        self.search_tree.heading("price", text="HARGA")
        self.search_tree.column("id",    width=70,  anchor="center", stretch=False)
        self.search_tree.column("name",  width=260, anchor="w",      stretch=True)
        self.search_tree.column("price", width=130, anchor="e",      stretch=False)
        self.search_tree.pack(fill=tk.BOTH, expand=True)

        self.search_tree.bind("<Return>",  self._tree_enter)
        self.search_tree.bind("<Escape>",  lambda e: self.search_entry.focus())
        self.search_tree.bind("<Double-1>", self._tree_enter)

        # ── Divider ──
        tk.Frame(body, bg=BORDER, width=1).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # ── Right panel: Cart ──
        right = tk.Frame(body, bg=BG, width=360)
        right.pack(side=tk.RIGHT, fill=tk.BOTH)
        right.pack_propagate(False)

        cart_header = tk.Frame(right, bg=CARD)
        cart_header.pack(fill=tk.X, pady=(0, 8))
        tk.Label(cart_header, text="🛒  KERANJANG", font=(font_main, 8, "bold"),
                 bg=CARD, fg=SUBTEXT).pack(side=tk.LEFT, padx=12, pady=10)
        self.item_count_lbl = tk.Label(cart_header, text="0 item",
                                        font=FONT_SMALL, bg=CARD, fg=SUBTEXT)
        self.item_count_lbl.pack(side=tk.RIGHT, padx=12)

        cart_card = tk.Frame(right, bg=CARD)
        cart_card.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        sb2 = ttk.Scrollbar(cart_card, style="Modern.Vertical.TScrollbar")
        sb2.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 2))

        self.cart_tree = ttk.Treeview(
            cart_card, style="Modern.Treeview",
            columns=("name", "qty", "subtotal"), show="headings",
            yscrollcommand=sb2.set, selectmode="browse")
        sb2.config(command=self.cart_tree.yview)

        self.cart_tree.heading("name",     text="PRODUK")
        self.cart_tree.heading("qty",      text="QTY")
        self.cart_tree.heading("subtotal", text="SUBTOTAL")
        self.cart_tree.column("name",     width=160, anchor="w",      stretch=True)
        self.cart_tree.column("qty",      width=45,  anchor="center", stretch=False)
        self.cart_tree.column("subtotal", width=110, anchor="e",      stretch=False)
        self.cart_tree.pack(fill=tk.BOTH, expand=True, padx=(8, 0), pady=8)

        self.cart_tree.bind("<Delete>",    self._remove_cart_item)
        self.cart_tree.bind("<BackSpace>", self._remove_cart_item)

        # Cart hint
        tk.Label(cart_card, text="Delete / ← pilih produk untuk hapus",
                 font=(font_main, 8), bg=CARD, fg=SUBTEXT).pack(pady=(0, 6))

        # Remove button
        rem_btn = tk.Button(right, text="✕  Hapus Item Dipilih",
                            font=FONT_SMALL, bg=CARD2, fg=SUBTEXT,
                            bd=0, relief="flat", padx=10, pady=7,
                            activebackground=DANGER, activeforeground="white",
                            cursor="hand2", command=self._remove_cart_item)
        rem_btn.pack(fill=tk.X, pady=(0, 8))

        # Total card
        total_card = tk.Frame(right, bg=CARD, pady=14)
        total_card.pack(fill=tk.X, pady=(0, 8))

        tk.Label(total_card, text="TOTAL", font=(font_main, 8, "bold"),
                 bg=CARD, fg=SUBTEXT).pack()
        self.total_label = tk.Label(total_card, text="Rp 0",
                                    font=(font_main, 22, "bold"),
                                    bg=CARD, fg=SUCCESS)
        self.total_label.pack(pady=(2, 0))

        # Checkout button
        self.pay_btn = tk.Button(
            right, text="Bayar  →",
            font=(font_main, 12, "bold"),
            bg=ACCENT2, fg="white",
            bd=0, relief="flat", pady=14,
            activebackground=ACCENT, activeforeground="white",
            cursor="hand2", command=self.checkout,
            state="disabled")
        self.pay_btn.pack(fill=tk.X)

        # ── Status bar ──
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill=tk.X)
        self.status_bar = tk.Label(self.root,
                                   text="Siap  ·  Ketik untuk mencari produk",
                                   font=(font_main, 8), bg=SURFACE, fg=SUBTEXT,
                                   anchor="w", padx=14, pady=5)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.search_entry.focus_set()

    def _update_clock(self):
        now = datetime.now().strftime("%a, %d %b %Y  %H:%M:%S")
        self.clock_label.config(text=now)
        self.root.after(1000, self._update_clock)

    # ── Search ───────────────────────────────────────────────────────────────

    def perform_search(self, *_):
        q = self.search_var.get().strip().lower()
        for row in self.search_tree.get_children():
            self.search_tree.delete(row)
        results = [p for p in self.data
                   if q in str(p.get('id', '')).lower()
                   or q in p.get('name', '').lower()]
        for p in results:
            self.search_tree.insert("", tk.END, iid=str(p['id']),
                                    values=(p['id'], p['name'], fmt_rp(p['price'])))
        count = len(results)
        self.status_bar.config(
            text=f"{count} produk ditemukan  ·  ↓ pilih dari daftar, Enter untuk tambah")

    def _search_enter(self, event=None):
        q = self.search_var.get().strip()
        # exact ID match first
        match = next((p for p in self.data if str(p['id']) == q), None)
        if not match:
            rows = self.search_tree.get_children()
            if len(rows) == 1:
                match = next((p for p in self.data
                              if str(p['id']) == self.search_tree.item(rows[0], "values")[0]), None)
        if match:
            self._add_to_cart(match)
        else:
            self._focus_results()

    def _focus_results(self, event=None):
        rows = self.search_tree.get_children()
        if rows:
            self.search_tree.selection_set(rows[0])
            self.search_tree.focus(rows[0])
            self.search_tree.focus_set()

    def _tree_enter(self, event=None):
        sel = self.search_tree.selection()
        if sel:
            p_id = self.search_tree.item(sel[0], "values")[0]
            prod = next((p for p in self.data if str(p['id']) == str(p_id)), None)
            if prod:
                self._add_to_cart(prod)
                self.search_entry.focus_set()

    def _clear_search(self, event=None):
        self.search_var.set("")
        self.search_entry.focus_set()

    # ── Cart ─────────────────────────────────────────────────────────────────

    def _add_to_cart(self, product):
        pid = product['id']
        if pid in self.cart:
            self.cart[pid]['qty'] += 1
        else:
            self.cart[pid] = {"product": product, "qty": 1}
        self._refresh_cart()
        self.search_var.set("")
        name = product['name']
        self.status_bar.config(
            text=f"✓  '{name}' ditambahkan ke keranjang  (qty: {self.cart[pid]['qty']})")

    def _remove_cart_item(self, event=None):
        sel = self.cart_tree.selection()
        if sel:
            pid = int(sel[0])
            if pid in self.cart:
                if self.cart[pid]['qty'] > 1:
                    self.cart[pid]['qty'] -= 1
                    self.status_bar.config(
                        text=f"Qty '{self.cart[pid]['product']['name']}' dikurangi")
                else:
                    name = self.cart[pid]['product']['name']
                    del self.cart[pid]
                    self.status_bar.config(text=f"'{name}' dihapus dari keranjang")
                self._refresh_cart()

    def _refresh_cart(self):
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)
        total = 0
        item_count = 0
        for pid, entry in self.cart.items():
            p   = entry['product']
            qty = entry['qty']
            sub = p['price'] * qty
            total += sub
            item_count += qty
            self.cart_tree.insert("", tk.END, iid=str(pid),
                                   values=(p['name'], qty, fmt_rp(sub)))
        self.total_label.config(text=fmt_rp(total))
        self.item_count_lbl.config(text=f"{item_count} item")
        state = "normal" if self.cart else "disabled"
        self.pay_btn.config(state=state)

    # ── Checkout ─────────────────────────────────────────────────────────────

    def checkout(self):
        if not self.cart or self._dialog_open:
            return
        self._dialog_open = True
        cart_list = [(v['product'], v['qty']) for v in self.cart.values()]
        CheckoutDialog(
            self.root, cart_list,
            on_confirm=self._finish_transaction,
            on_back=self._close_dialog)

    def _close_dialog(self):
        self._dialog_open = False

    def _finish_transaction(self):
        self._dialog_open = False
        self.cart.clear()
        self._refresh_cart()
        self.search_var.set("")
        self.search_entry.focus_set()
        self.status_bar.config(
            text=f"✓  Transaksi selesai  ·  {datetime.now().strftime('%H:%M:%S')}  ·  Siap transaksi baru")
        self.perform_search()


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app  = CashierApp(root)
    root.mainloop()