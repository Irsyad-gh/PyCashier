# Portable Cashier / finders - app to find products by ID
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
        self.root.title("Product Finder")
        self.root.geometry("900x650")
        
        self.data = []
        loaded_data = self.load_data()
        if loaded_data:
            self.data = loaded_data
            self.create_widgets()
        else:
            self.root.destroy()

    def load_data(self):
        """Membuka data.json menggunakan resource_path"""
        try:
            with open(resource_path("data.json"), "r", encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("Error", "Gagal memuat data.json")
            return None

    def create_widgets(self):
        tk.Label(self.root, text="PRODUCT FINDER", font=("Arial", 18, "bold"), bg="#2c3e50", fg="white", pady=10).pack(fill=tk.X)
        
        search_frame = ttk.Frame(self.root, padding=10)
        search_frame.pack(fill=tk.X)
        
        self.id_var = tk.StringVar()
        self.id_var.trace_add("write", lambda *a: self.perform_search())
        ttk.Entry(search_frame, textvariable=self.id_var, font=("Arial", 12)).pack(fill=tk.X)

        self.tree = ttk.Treeview(self.root, columns=("ID", "Nama", "Harga"), show='headings')
        self.tree.heading("ID", text="ID"); self.tree.heading("Nama", text="NAME"); self.tree.heading("Harga", text="PRICE")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.perform_search()

    def perform_search(self):
        query = self.id_var.get().strip()
        for item in self.tree.get_children(): self.tree.delete(item)
        for p in self.data:
            if query in str(p.get('id', '')):
                self.tree.insert("", tk.END, values=(p['id'], p['name'], p['price']))

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductFinderApp(root)
    root.mainloop()