# PyCashier / adder - app to add product data to the data.json file
# Copyright (C) 2026  Irsyad Dzaky Nurghany
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

def resource_path(filename):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

class ProductAdderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Portable Cashier - Product Management")
        self.root.geometry("1000x700")
        self.root.resizable(False, False)
        
        self.data = []
        # Menggunakan resource_path untuk menentukan lokasi file
        self.data_file = resource_path("data.json")
        
        if not self.load_data():
            messagebox.showerror("Error", f"Gagal memuat file data.json di:\n{self.data_file}")
            self.root.destroy()
            return
        
        try:
            self.create_widgets()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat antarmuka: {e}")
            self.root.destroy()

    def load_data(self):
        """Load data from JSON file menggunakan resource_path"""
        if not os.path.exists(self.data_file):
            return False

        try:
            with open(resource_path("data.json"), "r", encoding='utf-8') as f:
                self.data = json.load(f)
            
            if not isinstance(self.data, list):
                raise ValueError("JSON format must be an Array [ ]")
            return True
        except Exception as e:
            return False

    def save_data(self):
        """Save data to JSON file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")
            return False

    def create_widgets(self):
        header_label = tk.Label(
            self.root, text="PRODUCT MANAGEMENT - PORTABLE CASHIER",
            font=("Arial", 16, "bold"), bg="#2c3e50", fg="white", pady=15
        )
        header_label.pack(fill=tk.X)

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Form Tambah Produk
        form_frame = ttk.LabelFrame(main_frame, text=" Add New Product ", padding=15)
        form_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))

        ttk.Label(form_frame, text="Product ID:").grid(row=0, column=0, sticky="w", pady=5)
        self.id_entry = ttk.Entry(form_frame, font=("Arial", 11), width=20)
        self.id_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(form_frame, text="Product Name:").grid(row=1, column=0, sticky="w", pady=5)
        self.name_entry = ttk.Entry(form_frame, font=("Arial", 11), width=20)
        self.name_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(form_frame, text="Price (Rp):").grid(row=2, column=0, sticky="w", pady=5)
        self.price_entry = ttk.Entry(form_frame, font=("Arial", 11), width=20)
        self.price_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        ttk.Button(form_frame, text="Add Product", command=self.add_product).grid(row=3, column=0, columnspan=2, sticky="ew", pady=15)

        # Tabel Produk
        table_frame = ttk.LabelFrame(main_frame, text=" Product List ", padding=10)
        table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.product_tree = ttk.Treeview(
            table_frame, columns=("ID", "Nama", "Harga"),
            show='headings', yscrollcommand=scrollbar.set, height=20
        )
        scrollbar.config(command=self.product_tree.yview)

        self.product_tree.heading("ID", text="PRODUCT ID")
        self.product_tree.heading("Nama", text="PRODUCT NAME")
        self.product_tree.heading("Harga", text="PRICE (RP)")
        self.product_tree.column("ID", width=100, anchor="center")
        self.product_tree.column("Harga", width=150, anchor="e")
        self.product_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        btn_frame = ttk.Frame(table_frame)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_table).pack(side=tk.LEFT)

        self.status_label = tk.Label(self.root, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W, padx=10)
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)
        self.refresh_table()

    def validate_form(self):
        p_id, p_name, p_price = self.id_entry.get().strip(), self.name_entry.get().strip(), self.price_entry.get().strip()
        if not p_id.isdigit() or not p_name or not p_price.isdigit():
            messagebox.showwarning("Warning", "Input tidak valid!")
            return False
        return True

    def add_product(self):
        if not self.validate_form(): return
        new_item = {"id": int(self.id_entry.get()), "name": self.name_entry.get(), "price": int(self.price_entry.get())}
        self.data.append(new_item)
        if self.save_data():
            self.refresh_table()
            self.id_entry.delete(0, tk.END); self.name_entry.delete(0, tk.END); self.price_entry.delete(0, tk.END)

    def delete_product(self):
        selected = self.product_tree.selection()
        if not selected: return
        item_id = int(self.product_tree.item(selected[0], 'values')[0])
        self.data = [p for p in self.data if p.get('id') != item_id]
        if self.save_data(): self.refresh_table()

    def refresh_table(self):
        for item in self.product_tree.get_children(): self.product_tree.delete(item)
        for p in self.data:
            formatted_price = f"Rp {int(p.get('price', 0)):,.0f}".replace(",", ".")
            self.product_tree.insert("", tk.END, values=(p.get('id'), p.get('name'), formatted_price))
        self.status_label.config(text=f" Total Products: {len(self.data)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductAdderApp(root)
    root.mainloop()