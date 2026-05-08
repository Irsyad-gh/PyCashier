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


class ProductAdderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Portable Cashier - Product Management")
        self.root.geometry("1000x700")
        self.root.minsize(700, 500)
        self.root.resizable(True, True)

        self.data = []
        self.data_file = resource_path("data.json")

        if not self.load_data():
            messagebox.showerror(
                "Error",
                f"Gagal memuat file data.json di:\n{self.data_file}\n\n"
                "Pastikan file data.json berada di folder yang sama dengan adder.py"
            )
            self.root.destroy()
            return

        try:
            self.create_widgets()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat antarmuka:\n{e}")
            self.root.destroy()

    def load_data(self):
        """Load data from JSON file using resource_path."""
        if not os.path.exists(self.data_file):
            # Create an empty data.json if it doesn't exist
            try:
                with open(self.data_file, "w", encoding="utf-8") as f:
                    json.dump([], f)
                self.data = []
                return True
            except Exception:
                return False
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            if not isinstance(self.data, list):
                raise ValueError("Format JSON harus berupa Array [ ]")
            return True
        except Exception:
            return False

    def save_data(self):
        """Save data to JSON file."""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan file:\n{e}")
            return False

    def create_widgets(self):
        # ── Header ───────────────────────────────────────────────────────────
        tk.Label(
            self.root,
            text="PRODUCT MANAGEMENT - PORTABLE CASHIER",
            font=("Arial", 16, "bold"),
            bg="#2c3e50",
            fg="white",
            pady=15,
        ).pack(fill=tk.X)

        # ── Status bar (bottom) ───────────────────────────────────────────────
        self.status_label = tk.Label(
            self.root, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W, padx=10
        )
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)

        # ── Main area ────────────────────────────────────────────────────────
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # ── Left: Add form ────────────────────────────────────────────────────
        form_frame = ttk.LabelFrame(main_frame, text=" Add New Product ", padding=15)
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        form_frame.columnconfigure(1, weight=1)

        ttk.Label(form_frame, text="Product ID:").grid(row=0, column=0, sticky="w", pady=5)
        self.id_entry = ttk.Entry(form_frame, font=("Arial", 11), width=20)
        self.id_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(form_frame, text="Product Name:").grid(row=1, column=0, sticky="w", pady=5)
        self.name_entry = ttk.Entry(form_frame, font=("Arial", 11), width=20)
        self.name_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(form_frame, text="Price (Rp):").grid(row=2, column=0, sticky="w", pady=5)
        self.price_entry = ttk.Entry(form_frame, font=("Arial", 11), width=20)
        self.price_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # Allow pressing Enter in any field to submit
        for entry in (self.id_entry, self.name_entry, self.price_entry):
            entry.bind("<Return>", lambda _e: self.add_product())

        ttk.Button(
            form_frame, text="➕  Add Product", command=self.add_product
        ).grid(row=3, column=0, columnspan=2, sticky="ew", pady=15)

        ttk.Separator(form_frame, orient="horizontal").grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=5
        )

        ttk.Button(
            form_frame, text="🔄  Refresh", command=self.refresh_table
        ).grid(row=5, column=0, columnspan=2, sticky="ew", pady=3)

        ttk.Button(
            form_frame, text="🗑  Delete Selected", command=self.delete_product
        ).grid(row=6, column=0, columnspan=2, sticky="ew", pady=3)

        # ── Right: Product table ──────────────────────────────────────────────
        table_frame = ttk.LabelFrame(main_frame, text=" Product List ", padding=10)
        table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical")
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal")
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.product_tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Name", "Price"),
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            height=20,
        )
        scrollbar_y.config(command=self.product_tree.yview)
        scrollbar_x.config(command=self.product_tree.xview)

        self.product_tree.heading("ID", text="PRODUCT ID")
        self.product_tree.heading("Name", text="PRODUCT NAME")
        self.product_tree.heading("Price", text="PRICE (RP)")

        self.product_tree.column("ID", width=100, anchor="center")
        self.product_tree.column("Name", width=250)
        self.product_tree.column("Price", width=150, anchor="e")

        self.product_tree.pack(fill=tk.BOTH, expand=True)

        # Double-click to populate form for editing
        self.product_tree.bind("<Double-1>", self._on_row_double_click)

        self.refresh_table()

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _format_price(self, price: int) -> str:
        return f"Rp {price:,.0f}".replace(",", ".")

    def _on_row_double_click(self, event):
        """Fill form fields with the double-clicked row's data."""
        selected = self.product_tree.selection()
        if not selected:
            return
        values = self.product_tree.item(selected[0], "values")
        if len(values) < 3:
            return
        # Strip 'Rp ' prefix and dots for the raw price
        raw_price = values[2].replace("Rp ", "").replace(".", "")
        self.id_entry.delete(0, tk.END)
        self.id_entry.insert(0, values[0])
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, values[1])
        self.price_entry.delete(0, tk.END)
        self.price_entry.insert(0, raw_price)

    def validate_form(self):
        p_id = self.id_entry.get().strip()
        p_name = self.name_entry.get().strip()
        p_price = self.price_entry.get().strip()

        if not p_id.isdigit():
            messagebox.showwarning("Validasi", "Product ID harus berupa angka!")
            self.id_entry.focus_set()
            return False
        if not p_name:
            messagebox.showwarning("Validasi", "Nama produk tidak boleh kosong!")
            self.name_entry.focus_set()
            return False
        if not p_price.isdigit():
            messagebox.showwarning("Validasi", "Harga harus berupa angka (tanpa titik/koma)!")
            self.price_entry.focus_set()
            return False
        return True

    def add_product(self):
        if not self.validate_form():
            return

        new_id = int(self.id_entry.get().strip())
        # Check for duplicate ID
        if any(p.get("id") == new_id for p in self.data):
            messagebox.showwarning(
                "Duplikat", f"Produk dengan ID {new_id} sudah ada!\nGunakan ID yang berbeda."
            )
            return

        new_item = {
            "id": new_id,
            "name": self.name_entry.get().strip(),
            "price": int(self.price_entry.get().strip()),
        }
        self.data.append(new_item)

        if self.save_data():
            self.refresh_table()
            self.id_entry.delete(0, tk.END)
            self.name_entry.delete(0, tk.END)
            self.price_entry.delete(0, tk.END)
            self.id_entry.focus_set()
            self.status_label.config(
                text=f"  ✅ Produk '{new_item['name']}' berhasil ditambahkan."
            )

    def delete_product(self):
        selected = self.product_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Pilih produk yang ingin dihapus terlebih dahulu.")
            return
        values = self.product_tree.item(selected[0], "values")
        item_id = int(values[0])
        item_name = values[1]

        confirm = messagebox.askyesno(
            "Konfirmasi", f"Hapus produk '{item_name}' (ID: {item_id})?"
        )
        if not confirm:
            return

        self.data = [p for p in self.data if p.get("id") != item_id]
        if self.save_data():
            self.refresh_table()
            self.status_label.config(text=f"  🗑 Produk '{item_name}' berhasil dihapus.")

    def refresh_table(self):
        for row in self.product_tree.get_children():
            self.product_tree.delete(row)
        for p in self.data:
            self.product_tree.insert(
                "", tk.END,
                values=(p.get("id"), p.get("name"), self._format_price(int(p.get("price", 0))))
            )
        self.status_label.config(text=f"  Total Produk: {len(self.data)}")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    setup_dpi_awareness()
    root = tk.Tk()
    app = ProductAdderApp(root)
    root.mainloop()