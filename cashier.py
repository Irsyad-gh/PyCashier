# PyCashier / cashier - app to find products by ID and add up the total price
# Copyright (C) 2026  Irsyad Dzaky Nurghany

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys

def resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

class ProductFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Portable Cashier - Cash Register")
        self.root.geometry("1000x700")
        self.root.resizable(False, False)
        
        self.data = []
        self.cart = []
        
        loaded_data = self.load_data()
        if loaded_data is None:
            self.root.after(100, self.root.destroy)
            return
        
        self.data = loaded_data
        self.create_widgets()

    def load_data(self):
        """Memuat data menggunakan resource_path"""
        try:
            with open(resource_path("data.json"), "r", encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat data.json: {e}")
            return None

    def create_widgets(self):
        title_label = tk.Label(self.root, text="PORTABLE CASHIER - CASH REGISTER", 
                               font=("Arial", 18, "bold"), bg="#2c3e50", fg="white", pady=15)
        title_label.pack(fill=tk.X)

        search_frame = ttk.LabelFrame(self.root, text=" Find Product ", padding=20)
        search_frame.pack(fill=tk.X, padx=15, pady=10)

        self.id_var = tk.StringVar()
        self.id_var.trace_add("write", lambda *a: self.perform_search())
        self.id_entry = ttk.Entry(search_frame, textvariable=self.id_var, font=("Arial", 12))
        self.id_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.id_entry.bind('<Return>', self.add_to_cart)

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15)

        # Tabel Hasil Pencarian
        left_frame = ttk.LabelFrame(main_frame, text=" Search Results ", padding=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.search_tree = ttk.Treeview(left_frame, columns=("ID", "Nama", "Harga"), show='headings', height=10)
        self.search_tree.heading("ID", text="ID"); self.search_tree.heading("Nama", text="NAME"); self.search_tree.heading("Harga", text="PRICE")
        self.search_tree.pack(fill=tk.BOTH, expand=True)
        ttk.Button(left_frame, text="Add Selected to Cart", command=self.add_selected_to_cart).pack(fill=tk.X)

        # Tabel Keranjang
        right_frame = ttk.LabelFrame(main_frame, text=" Shopping Cart ", padding=5)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.cart_tree = ttk.Treeview(right_frame, columns=("ID", "Nama", "Harga", "Qty"), show='headings', height=10)
        self.cart_tree.heading("ID", text="ID"); self.cart_tree.heading("Nama", text="NAME"); self.cart_tree.heading("Qty", text="QTY")
        self.cart_tree.pack(fill=tk.BOTH, expand=True)

        # Total & Checkout
        total_frame = ttk.Frame(self.root, padding=10)
        total_frame.pack(fill=tk.X)
        self.total_label = tk.Label(total_frame, text="Total: Rp 0", font=("Arial", 16, "bold"), fg="green")
        self.total_label.pack(side=tk.LEFT)
        ttk.Button(total_frame, text="Pay & Reset", command=self.checkout).pack(side=tk.RIGHT)

        self.perform_search()

    def perform_search(self):
        query = self.id_var.get().strip()
        results = [p for p in self.data if query in str(p.get('id', ''))]
        for item in self.search_tree.get_children(): self.search_tree.delete(item)
        for p in results:
            self.search_tree.insert("", tk.END, values=(p['id'], p['name'], p['price']))

    def add_to_cart(self, event=None):
        query = self.id_var.get().strip()
        product = next((p for p in self.data if str(p['id']) == query), None)
        if product:
            self.cart.append(product)
            self.update_cart_display()
            self.id_var.set("")

    def add_selected_to_cart(self):
        selected = self.search_tree.selection()
        if selected:
            p_id = self.search_tree.item(selected[0], 'values')[0]
            self.id_var.set(p_id)
            self.add_to_cart()

    def update_cart_display(self):
        for item in self.cart_tree.get_children(): self.cart_tree.delete(item)
        total = 0
        for p in self.cart:
            self.cart_tree.insert("", tk.END, values=(p['id'], p['name'], p['price'], 1))
            total += p['price']
        self.total_label.config(text=f"Total: Rp {total:,.0f}".replace(",", "."))

    def checkout(self):
        if self.cart:
            messagebox.showinfo("Success", "Transaksi Berhasil!")
            self.cart = []; self.update_cart_display()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductFinderApp(root)
    root.mainloop()