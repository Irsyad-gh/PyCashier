# Portable Cashier / finders - app to find products by ID
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
            windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                windll.user32.SetProcessDPIAware()
            except Exception:
                pass


class ProductFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Portable Cashier - Product Finder")
        self.root.geometry("900x650")
        self.root.minsize(600, 400)
        self.root.resizable(True, True)

        self.data = []
        loaded_data = self.load_data()
        if loaded_data is not None:
            self.data = loaded_data
            self.create_widgets()
        else:
            self.root.after(100, self.root.destroy)

    def load_data(self):
        """Load data.json using resource_path."""
        path = resource_path("data.json")
        if not os.path.exists(path):
            messagebox.showerror(
                "Error",
                f"File data.json tidak ditemukan di:\n{path}\n\n"
                "Pastikan file data.json berada di folder yang sama dengan finders.py"
            )
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat data.json:\n{e}")
            return None

    def _format_price(self, price) -> str:
        return f"Rp {int(price):,.0f}".replace(",", ".")

    def create_widgets(self):
        # ── Header ───────────────────────────────────────────────────────────
        tk.Label(
            self.root,
            text="PRODUCT FINDER",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white",
            pady=12,
        ).pack(fill=tk.X)

        # ── Search bar ───────────────────────────────────────────────────────
        search_frame = ttk.Frame(self.root, padding=10)
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text="Search by ID:").pack(side=tk.LEFT, padx=(0, 5))

        self.id_var = tk.StringVar()
        self.id_var.trace_add("write", lambda *_: self.perform_search())

        ttk.Entry(
            search_frame, textvariable=self.id_var, font=("Arial", 12)
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # ── Results table ─────────────────────────────────────────────────────
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical")
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Name", "Price"),
            show="headings",
            yscrollcommand=scrollbar_y.set,
        )
        scrollbar_y.config(command=self.tree.yview)

        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="NAME")
        self.tree.heading("Price", text="PRICE")

        self.tree.column("ID", width=90, anchor="center")
        self.tree.column("Name", width=300)
        self.tree.column("Price", width=160, anchor="e")

        self.tree.pack(fill=tk.BOTH, expand=True)

        # ── Status bar ────────────────────────────────────────────────────────
        self.status_label = tk.Label(
            self.root, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W, padx=10
        )
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)

        self.perform_search()

    def perform_search(self):
        query = self.id_var.get().strip()
        for row in self.tree.get_children():
            self.tree.delete(row)

        results = [p for p in self.data if query in str(p.get("id", ""))]
        for p in results:
            self.tree.insert(
                "", tk.END,
                values=(p["id"], p["name"], self._format_price(p["price"]))
            )
        self.status_label.config(
            text=f"  Menampilkan {len(results)} dari {len(self.data)} produk"
        )


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    setup_dpi_awareness()
    root = tk.Tk()
    app = ProductFinderApp(root)
    root.mainloop()