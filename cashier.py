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
import platform


def resource_path(filename):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


def setup_dpi_awareness():
    """Enable High-DPI awareness on Windows so the UI doesn't look blurry."""
    if platform.system() == "Windows":
        try:
            from ctypes import windll
            # Try the newer Per-Monitor V2 mode first (Windows 10 1703+)
            windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                windll.user32.SetProcessDPIAware()
            except Exception:
                pass


class ProductFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Portable Cashier - Cash Register")
        self.root.geometry("1000x700")
        self.root.minsize(700, 500)
        self.root.resizable(True, True)

        self.data = []
        self.cart = []

        loaded_data = self.load_data()
        if loaded_data is None:
            self.root.after(100, self.root.destroy)
            return
        self.data = loaded_data

        self.create_widgets()

    def load_data(self):
        """Load product data from data.json using resource_path."""
        path = resource_path("data.json")
        if not os.path.exists(path):
            messagebox.showerror(
                "Error",
                f"File data.json tidak ditemukan di:\n{path}\n\n"
                "Pastikan file data.json berada di folder yang sama dengan cashier.py"
            )
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("Format JSON harus berupa Array [ ]")
            return data
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat data.json:\n{e}")
            return None

    def create_widgets(self):
        # ── Header ───────────────────────────────────────────────────────────
        tk.Label(
            self.root,
            text="PORTABLE CASHIER - CASH REGISTER",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white",
            pady=15,
        ).pack(fill=tk.X)

        # ── Search bar ───────────────────────────────────────────────────────
        search_frame = ttk.LabelFrame(self.root, text=" Find Product ", padding=10)
        search_frame.pack(fill=tk.X, padx=15, pady=(10, 0))

        ttk.Label(search_frame, text="Search by ID:").pack(side=tk.LEFT, padx=(0, 5))

        self.id_var = tk.StringVar()
        self.id_var.trace_add("write", lambda *_: self.perform_search())

        self.id_entry = ttk.Entry(search_frame, textvariable=self.id_var, font=("Arial", 12))
        self.id_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.id_entry.bind("<Return>", self.add_to_cart)

        ttk.Button(
            search_frame, text="Add (Enter)", command=self.add_to_cart
        ).pack(side=tk.LEFT, padx=5)

        # ── Total & Checkout  ← IMPORTANT: pack this BEFORE the expanding
        #    main_frame so it is always visible at the bottom ─────────────────
        total_frame = ttk.Frame(self.root, padding=(15, 8))
        total_frame.pack(fill=tk.X, side=tk.BOTTOM)

        ttk.Separator(self.root, orient="horizontal").pack(fill=tk.X, side=tk.BOTTOM)

        ttk.Button(
            total_frame, text="🗑  Remove Selected", command=self.remove_from_cart
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            total_frame, text="💳  Pay & Reset", command=self.checkout
        ).pack(side=tk.RIGHT, padx=5)

        self.total_label = tk.Label(
            total_frame,
            text="Total: Rp 0",
            font=("Arial", 16, "bold"),
            fg="#27ae60",
        )
        self.total_label.pack(side=tk.LEFT)

        # ── Main area (search results + cart) ────────────────────────────────
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)

        # Left: Search Results
        left_frame = ttk.LabelFrame(main_frame, text=" Search Results ", padding=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.search_tree = ttk.Treeview(
            left_frame,
            columns=("ID", "Name", "Price"),
            show="headings",
            height=15,
            selectmode="browse",
        )
        self.search_tree.heading("ID", text="ID")
        self.search_tree.heading("Name", text="NAME")
        self.search_tree.heading("Price", text="PRICE")
        self.search_tree.column("ID", width=80, anchor="center")
        self.search_tree.column("Name", width=180)
        self.search_tree.column("Price", width=120, anchor="e")

        s_scroll = ttk.Scrollbar(left_frame, orient="vertical", command=self.search_tree.yview)
        self.search_tree.configure(yscrollcommand=s_scroll.set)
        s_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.search_tree.pack(fill=tk.BOTH, expand=True)

        ttk.Button(
            left_frame, text="➕  Add Selected to Cart", command=self.add_selected_to_cart
        ).pack(fill=tk.X, pady=(5, 0))

        # Right: Cart
        right_frame = ttk.LabelFrame(main_frame, text=" Shopping Cart ", padding=5)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.cart_tree = ttk.Treeview(
            right_frame,
            columns=("ID", "Name", "Price", "Qty"),
            show="headings",
            height=15,
            selectmode="browse",
        )
        self.cart_tree.heading("ID", text="ID")
        self.cart_tree.heading("Name", text="NAME")
        self.cart_tree.heading("Price", text="PRICE")
        self.cart_tree.heading("Qty", text="QTY")
        self.cart_tree.column("ID", width=60, anchor="center")
        self.cart_tree.column("Name", width=160)
        self.cart_tree.column("Price", width=110, anchor="e")
        self.cart_tree.column("Qty", width=50, anchor="center")

        c_scroll = ttk.Scrollbar(right_frame, orient="vertical", command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=c_scroll.set)
        c_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.cart_tree.pack(fill=tk.BOTH, expand=True)

        # Initial population
        self.perform_search()

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _format_price(self, price: int) -> str:
        """Format integer price to IDR string, e.g. Rp 12.500"""
        return f"Rp {price:,.0f}".replace(",", ".")

    def perform_search(self):
        query = self.id_var.get().strip()
        for row in self.search_tree.get_children():
            self.search_tree.delete(row)
        for p in self.data:
            if query in str(p.get("id", "")):
                self.search_tree.insert(
                    "", tk.END,
                    values=(p["id"], p["name"], self._format_price(p["price"]))
                )

    def add_to_cart(self, event=None):
        query = self.id_var.get().strip()
        product = next((p for p in self.data if str(p["id"]) == query), None)
        if product:
            self.cart.append(product)
            self.update_cart_display()
            self.id_var.set("")
            self.id_entry.focus_set()
        else:
            messagebox.showwarning("Not Found", f"Produk dengan ID '{query}' tidak ditemukan.")

    def add_selected_to_cart(self):
        selected = self.search_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Pilih produk dari tabel hasil pencarian terlebih dahulu.")
            return
        p_id = self.search_tree.item(selected[0], "values")[0]
        self.id_var.set(str(p_id))
        self.add_to_cart()

    def remove_from_cart(self):
        """Remove the selected item from the cart."""
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Pilih item di keranjang yang ingin dihapus.")
            return
        # Determine the index in self.cart from the Treeview row index
        all_rows = self.cart_tree.get_children()
        idx = list(all_rows).index(selected[0])
        if 0 <= idx < len(self.cart):
            del self.cart[idx]
            self.update_cart_display()

    def update_cart_display(self):
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)

        # Aggregate items with qty
        aggregated = {}
        for p in self.cart:
            pid = p["id"]
            if pid in aggregated:
                aggregated[pid]["qty"] += 1
            else:
                aggregated[pid] = {**p, "qty": 1}

        total = 0
        for item in aggregated.values():
            subtotal = item["price"] * item["qty"]
            self.cart_tree.insert(
                "", tk.END,
                values=(item["id"], item["name"], self._format_price(item["price"]), item["qty"])
            )
            total += subtotal

        self.total_label.config(text=f"Total: {self._format_price(total)}")

    def checkout(self):
        if not self.cart:
            messagebox.showinfo("Info", "Keranjang masih kosong!")
            return
        total = sum(p["price"] for p in self.cart)
        confirm = messagebox.askyesno(
            "Konfirmasi Pembayaran",
            f"Total pembayaran: {self._format_price(total)}\n\nLanjutkan transaksi?"
        )
        if confirm:
            messagebox.showinfo("Sukses", "✅ Transaksi Berhasil!\nTerima kasih.")
            self.cart = []
            self.update_cart_display()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    setup_dpi_awareness()
    root = tk.Tk()
    app = ProductFinderApp(root)
    root.mainloop()