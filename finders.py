# Portable Cashier / finders - app to find products by ID
# Copyright (C) 2026  Irsyad Dzaky Nurghany

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys

class ProductFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Product Finder")
        self.root.geometry("900x650")
        self.root.resizable(False, False)
        
        # Initialize data as empty list to prevent attribute error
        self.data = []
        
        # Load data
        loaded_data = self.load_data()
        if loaded_data is None:
            # Error message already handled in load_data, but we ensure app doesn't continue
            self.root.after(100, self.root.destroy) 
            return
        
        self.data = loaded_data
        
        # Create GUI
        try:
            self.create_widgets()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create interface: {e}")
            self.root.destroy()

    def load_data(self):
        """Search and load data from data.json"""
        # Search for absolute path to avoid confusion when running from terminal/shortcut
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_path, 'data.json')

        if not os.path.exists(file_path):
            messagebox.showerror("Error", f"File 'data.json' not found at:\n{file_path}")
            return None

        try:
            # Use utf-8 encoding to support special characters
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise ValueError("JSON format must be an Array [ ]")

            # Minimal data structure validation
            for item in data:
                if not all(k in item for k in ('id', 'name', 'price')):
                    raise ValueError("Each product must have 'id', 'name', and 'price'")
            
            return data
            
        except json.JSONDecodeError:
            messagebox.showerror("Error", "data.json file is corrupted or invalid format.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        return None

    def create_widgets(self):
        # Header / Title
        title_label = tk.Label(
            self.root, text="PRODUCT FINDER", 
            font=("Arial", 18, "bold"), bg="#2c3e50", fg="white", pady=15
        )
        title_label.pack(fill=tk.X)

        # Search Frame
        search_frame = ttk.LabelFrame(self.root, text=" Search Filter ", padding=20)
        search_frame.pack(fill=tk.X, padx=15, pady=10)

        ttk.Label(search_frame, text="Enter Product ID:", font=("Arial", 11)).grid(row=0, column=0, sticky="w")
        
        self.id_var = tk.StringVar()
        self.id_var.trace_add("write", self.on_search_changed)
        
        self.id_entry = ttk.Entry(search_frame, textvariable=self.id_var, font=("Arial", 12))
        self.id_entry.grid(row=0, column=1, padx=10, sticky="ew")
        self.id_entry.focus()

        ttk.Button(search_frame, text="Reset", command=self.reset_search).grid(row=0, column=2, padx=5)
        search_frame.columnconfigure(1, weight=1)

        # Treeview (Table)
        tree_frame = ttk.Frame(self.root, padding=10)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(
            tree_frame, columns=("ID", "Nama", "Harga"), 
            show='headings', yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.tree.yview)

        # Headings & Columns
        self.tree.heading("ID", text="PRODUCT ID")
        self.tree.heading("Nama", text="PRODUCT NAME")
        self.tree.heading("Harga", text="PRICE (RP)")

        self.tree.column("ID", width=100, anchor="center")
        self.tree.column("Nama", width=450, anchor="w")
        self.tree.column("Harga", width=150, anchor="e")

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Status Bar
        self.status_label = tk.Label(self.root, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W, padx=10)
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)

        # Display initial data
        self.display_results(self.data)

    def on_search_changed(self, *args):
        # Remove non-digit characters automatically
        val = self.id_var.get()
        if not val.isdigit() and val != "":
            self.id_var.set(''.join(filter(str.isdigit, val)))
        self.perform_search()

    def perform_search(self):
        query = self.id_var.get().strip()
        
        if not query:
            self.display_results(self.data)
            return

        # Flexible search: Find products whose ID contains the entered digits
        # (Change k == int(query) if you want exact match search)
        results = [p for p in self.data if query in str(p.get('id', ''))]
        self.display_results(results)

    def display_results(self, products):
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert data
        for p in products:
            try:
                # Format Rupiah with thousands separator dot
                price = int(p.get('price', 0))
                formatted_price = f"Rp {price:,.0f}".replace(",", ".")
                
                self.tree.insert("", tk.END, values=(
                    str(p.get('id')).zfill(3), 
                    p.get('name', 'N/A').upper(), 
                    formatted_price
                ))
            except:
                continue

        # Update Status
        self.status_label.config(text=f" Showing {len(products)} products")

    def reset_search(self):
        self.id_var.set("")
        self.id_entry.focus()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductFinderApp(root)
    root.mainloop()