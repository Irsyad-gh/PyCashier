# Portable Cashier / adder - app to add product data to the data.json file
# Copyright (C) 2026  Irsyad Dzaky Nurghany
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys


class ProductAdderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Portable Cashier - Product Management")
        self.root.geometry("1000x700")
        self.root.resizable(False, False)
        
        # Inisialisasi data
        self.data = []
        self.data_file = self.find_data_file()
        
        # Load data dari file
        if not self.load_data():
            messagebox.showerror("Error", "Gagal memuat file data.json")
            self.root.destroy()
            return
        
        # Buat GUI
        try:
            self.create_widgets()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat antarmuka: {e}")
            self.root.destroy()

    def find_data_file(self):
        """Find data.json file"""
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, 'data.json')

    def load_data(self):
        """Load data from JSON file"""
        if not os.path.exists(self.data_file):
            messagebox.showerror("Error", f"data.json file not found:\n{self.data_file}")
            return False

        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            
            if not isinstance(self.data, list):
                raise ValueError("JSON format must be an Array [ ]")
            
            return True
        except json.JSONDecodeError:
            messagebox.showerror("Error", "data.json file is corrupted or invalid format")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {e}")
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
        """Membuat interface aplikasi"""
        # ===== Header =====
        header_label = tk.Label(
            self.root,
            text="PRODUCT MANAGEMENT - PORTABLE CASHIER",
            font=("Arial", 16, "bold"),
            bg="#2c3e50",
            fg="white",
            pady=15
        )
        header_label.pack(fill=tk.X)

        # ===== Main Frame =====
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # ===== Left Frame - Form Tambah Produk =====
        form_frame = ttk.LabelFrame(main_frame, text=" Add New Product ", padding=15)
        form_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))

        # ID Input
        ttk.Label(form_frame, text="Product ID:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.id_entry = ttk.Entry(form_frame, font=("Arial", 11), width=20)
        self.id_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Nama Produk Input
        ttk.Label(form_frame, text="Product Name:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.name_entry = ttk.Entry(form_frame, font=("Arial", 11), width=20)
        self.name_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Harga Input
        ttk.Label(form_frame, text="Price (Rp):", font=("Arial", 10)).grid(row=2, column=0, sticky="w", pady=5)
        self.price_entry = ttk.Entry(form_frame, font=("Arial", 11), width=20)
        self.price_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # Button Tambah Produk
        add_btn = ttk.Button(form_frame, text="Add Product", command=self.add_product)
        add_btn.grid(row=3, column=0, columnspan=2, sticky="ew", pady=15)

        # Separator
        ttk.Separator(form_frame, orient='horizontal').grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)

        # Info Label
        info_text = """
Instruction:
• Product ID: Unique number (digits)
• Product Name: Product name
• Price: Price in Rupiah

Press 'Add Product'
to save to
database
        """
        info_label = tk.Label(form_frame, text=info_text, justify=tk.LEFT, font=("Arial", 9), fg="gray")
        info_label.grid(row=5, column=0, columnspan=2, sticky="ew", pady=10)

        form_frame.columnconfigure(1, weight=1)

        # ===== Right Frame - Daftar Produk =====
        table_frame = ttk.LabelFrame(main_frame, text=" Product List ", padding=10)
        table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Treeview untuk menampilkan produk
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.product_tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Nama", "Harga"),
            show='headings',
            yscrollcommand=scrollbar.set,
            height=20
        )
        scrollbar.config(command=self.product_tree.yview)

        # Konfigurasi kolom
        self.product_tree.heading("ID", text="PRODUCT ID")
        self.product_tree.heading("Nama", text="PRODUCT NAME")
        self.product_tree.heading("Harga", text="PRICE (RP)")

        self.product_tree.column("ID", width=120, anchor="center")
        self.product_tree.column("Nama", width=250, anchor="w")
        self.product_tree.column("Harga", width=150, anchor="e")

        self.product_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Button Hapus Produk
        button_frame = ttk.Frame(table_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Delete Selected Product", command=self.delete_product).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Refresh", command=self.refresh_table).pack(side=tk.LEFT)

        # ===== Status Bar =====
        self.status_label = tk.Label(self.root, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W, padx=10, pady=5)
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)

        # Load and display data
        self.refresh_table()

    def validate_form(self):
        """Validate form input"""
        product_id = self.id_entry.get().strip()
        product_name = self.name_entry.get().strip()
        product_price = self.price_entry.get().strip()

        # Validasi ID
        if not product_id:
            messagebox.showwarning("Warning", "Product ID cannot be empty!")
            self.id_entry.focus()
            return False

        if not product_id.isdigit():
            messagebox.showwarning("Warning", "Product ID must be a number!")
            self.id_entry.focus()
            return False

        # Check for duplicate ID
        for item in self.data:
            if str(item.get('id', '')) == product_id:
                messagebox.showwarning("Warning", "Product ID already exists in database!")
                self.id_entry.focus()
                return False

        # Validate Name
        if not product_name:
            messagebox.showwarning("Warning", "Product Name cannot be empty!")
            self.name_entry.focus()
            return False

        # Validate Price
        if not product_price:
            messagebox.showwarning("Warning", "Price cannot be empty!")
            self.price_entry.focus()
            return False

        if not product_price.isdigit():
            messagebox.showwarning("Warning", "Price must be a number!")
            self.price_entry.focus()
            return False

        if int(product_price) <= 0:
            messagebox.showwarning("Warning", "Price must be greater than 0!")
            self.price_entry.focus()
            return False

        return True

    def add_product(self):
        """Add new product"""
        if not self.validate_form():
            return

        product_id = int(self.id_entry.get().strip())
        product_name = self.name_entry.get().strip()
        product_price = int(self.price_entry.get().strip())

        # Add product to data
        new_product = {
            "id": product_id,
            "name": product_name,
            "price": product_price
        }
        self.data.append(new_product)

        # Save to file
        if self.save_data():
            messagebox.showinfo("Success", f"Product '{product_name}' has been added successfully!")
            
            # Clear form
            self.id_entry.delete(0, tk.END)
            self.name_entry.delete(0, tk.END)
            self.price_entry.delete(0, tk.END)
            self.id_entry.focus()

            # Refresh table
            self.refresh_table()
        else:
            # If failed, remove from data
            self.data.pop()
            messagebox.showerror("Error", "Failed to save product to file!")

    def delete_product(self):
        """Delete selected product"""
        selected_item = self.product_tree.selection()
        
        if not selected_item:
            messagebox.showwarning("Warning", "Select a product to delete!")
            return

        # Get data of selected product
        item_values = self.product_tree.item(selected_item[0], 'values')
        product_id = int(item_values[0])
        product_name = item_values[1]

        # Confirm deletion
        if not messagebox.askyesno("Confirmation", f"Delete product '{product_name}' from database?"):
            return

        # Find and delete product from data
        for i, item in enumerate(self.data):
            if item.get('id') == product_id:
                self.data.pop(i)
                break

        # Save to file
        if self.save_data():
            messagebox.showinfo("Success", f"Product '{product_name}' has been deleted successfully!")
            self.refresh_table()
        else:
            messagebox.showerror("Error", "Failed to save changes to file!")

    def refresh_table(self):
        """Refresh product table display"""
        # Clear table
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)

        # Insert product data
        for product in self.data:
            try:
                product_id = str(product.get('id', 'N/A'))
                product_name = product.get('name', 'N/A')
                product_price = int(product.get('price', 0))
                
                # Format harga
                formatted_price = f"Rp {product_price:,.0f}".replace(",", ".")
                
                self.product_tree.insert("", tk.END, values=(
                    product_id,
                    product_name,
                    formatted_price
                ))
            except:
                continue

        # Update status
        self.status_label.config(text=f" Total Products: {len(self.data)} items")


def main():
    root = tk.Tk()
    app = ProductAdderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

