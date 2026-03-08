# Portable Cashier / cashier - app to find products by ID and add up the total price
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

class ProductFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Portable Cashier - Cash Register")
        self.root.geometry("1000x700")
        self.root.resizable(False, False)
        
        # Inisialisasi data sebagai list kosong untuk mencegah error atribut
        self.data = []
        
        # Initialize shopping cart
        self.cart = []  # List to store selected products
        
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
            self.root, text="PORTABLE CASHIER - CASH REGISTER", 
            font=("Arial", 18, "bold"), bg="#2c3e50", fg="white", pady=15
        )
        title_label.pack(fill=tk.X)

        # Search Frame
        search_frame = ttk.LabelFrame(self.root, text=" Find Product ", padding=20)
        search_frame.pack(fill=tk.X, padx=15, pady=10)

        ttk.Label(search_frame, text="Enter Product ID:", font=("Arial", 11)).grid(row=0, column=0, sticky="w")
        
        self.id_var = tk.StringVar()
        self.id_var.trace_add("write", self.on_search_changed)
        
        self.id_entry = ttk.Entry(search_frame, textvariable=self.id_var, font=("Arial", 12))
        self.id_entry.grid(row=0, column=1, padx=10, sticky="ew")
        self.id_entry.focus()
        
        # Bind Enter key to add product to cart
        self.id_entry.bind('<Return>', self.add_to_cart)

        ttk.Button(search_frame, text="Reset", command=self.reset_search).grid(row=0, column=2, padx=5)
        search_frame.columnconfigure(1, weight=1)

        # Main content frame (split view)
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Left frame - Product search results
        left_frame = ttk.LabelFrame(main_frame, text=" Search Results ", padding=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Treeview for search results
        self.search_tree = ttk.Treeview(
            left_frame, columns=("ID", "Nama", "Harga"), 
            show='headings', height=12
        )

        # Headings & Columns for search results
        self.search_tree.heading("ID", text="ID")
        self.search_tree.heading("Nama", text="PRODUCT NAME")
        self.search_tree.heading("Harga", text="PRICE")

        self.search_tree.column("ID", width=80, anchor="center")
        self.search_tree.column("Nama", width=200, anchor="w")
        self.search_tree.column("Harga", width=120, anchor="e")

        self.search_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        # Button to add to cart
        ttk.Button(left_frame, text="Add to Cart", command=self.add_selected_to_cart).pack(fill=tk.X)

        # Right frame - Shopping cart
        right_frame = ttk.LabelFrame(main_frame, text=" Shopping Cart ", padding=5)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Treeview untuk keranjang belanja
        cart_frame = ttk.Frame(right_frame)
        cart_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(cart_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.cart_tree = ttk.Treeview(
            cart_frame, columns=("ID", "Nama", "Harga", "Qty"), 
            show='headings', yscrollcommand=scrollbar.set, height=12
        )
        scrollbar.config(command=self.cart_tree.yview)

        # Headings & Columns for cart
        self.cart_tree.heading("ID", text="ID")
        self.cart_tree.heading("Nama", text="PRODUCT NAME")
        self.cart_tree.heading("Harga", text="PRICE")
        self.cart_tree.heading("Qty", text="QTY")

        self.cart_tree.column("ID", width=60, anchor="center")
        self.cart_tree.column("Nama", width=150, anchor="w")
        self.cart_tree.column("Harga", width=100, anchor="e")
        self.cart_tree.column("Qty", width=50, anchor="center")

        self.cart_tree.pack(fill=tk.BOTH, expand=True)

        # Cart control buttons
        cart_buttons = ttk.Frame(right_frame)
        cart_buttons.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(cart_buttons, text="Delete Item", command=self.remove_from_cart).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cart_buttons, text="Clear Cart", command=self.clear_cart).pack(side=tk.LEFT)

        # Total frame
        total_frame = ttk.LabelFrame(self.root, text=" Total Purchase ", padding=10)
        total_frame.pack(fill=tk.X, padx=15, pady=10)

        self.total_label = tk.Label(total_frame, text="Total: Rp 0", font=("Arial", 16, "bold"), fg="green")
        self.total_label.pack(side=tk.LEFT)

        ttk.Button(total_frame, text="Calculate Total", command=self.calculate_total).pack(side=tk.RIGHT)
        ttk.Button(total_frame, text="Pay & Reset", command=self.checkout).pack(side=tk.RIGHT, padx=(5, 0))

        # Status Bar
        self.status_label = tk.Label(self.root, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W, padx=10)
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)

        # Display initial data
        self.display_results(self.data)

    def on_search_changed(self, *args):
        """Called when product ID input changes"""
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
        # Clear search table
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)

        # Insert data to search table
        for p in products:
            try:
                # Format Rupiah with thousands separator dot
                price = int(p.get('price', 0))
                formatted_price = f"Rp {price:,.0f}".replace(",", ".")
                
                self.search_tree.insert("", tk.END, values=(
                    str(p.get('id')).zfill(3), 
                    p.get('name', 'N/A'), 
                    formatted_price
                ))
            except:
                continue

        # Update Status
        self.status_label.config(text=f" Showing {len(products)} products from {len(self.data)} total products")

    def reset_search(self):
        self.id_var.set("")
        self.id_entry.focus()

    def add_to_cart(self, event=None):
        """Add product to cart by pressing Enter"""
        query = self.id_var.get().strip()
        
        if not query or not query.isdigit():
            messagebox.showwarning("Warning", "Enter a valid product ID (number)")
            return
        
        # Find product by exact ID match
        product = None
        for p in self.data:
            if str(p.get('id', '')) == query:
                product = p
                break
        
        if product is None:
            messagebox.showerror("Error", f"Product with ID {query} not found!")
            return
        
        # Add to cart (or add quantity if already exists)
        product_found = False
        for cart_item in self.cart:
            if cart_item['id'] == product['id']:
                cart_item['quantity'] += 1
                product_found = True
                break
        
        if not product_found:
            self.cart.append({
                'id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'quantity': 1
            })
        
        # Update cart display
        self.update_cart_display()
        
        # Reset input and focus
        self.id_var.set("")
        self.id_entry.focus()
        
        # Success message
        messagebox.showinfo("Success", f"Product '{product['name']}' has been added to cart!")

    def add_selected_to_cart(self):
        """Add product selected from search results to cart"""
        selected_item = self.search_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Select a product from the search results first!")
            return
        
        # Get product data from selected item
        item_values = self.search_tree.item(selected_item[0], 'values')
        product_id = int(item_values[0])  # ID is already in 3-digit format
        
        # Find original product from data
        product = None
        for p in self.data:
            if p.get('id') == product_id:
                product = p
                break
        
        if product is None:
            messagebox.showerror("Error", "Product not found in database!")
            return
        
        # Add to cart
        product_found = False
        for cart_item in self.cart:
            if cart_item['id'] == product['id']:
                cart_item['quantity'] += 1
                product_found = True
                break
        
        if not product_found:
            self.cart.append({
                'id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'quantity': 1
            })
        
        # Update cart display
        self.update_cart_display()
        
        messagebox.showinfo("Success", f"Product '{product['name']}' has been added to cart!")

    def remove_from_cart(self):
        """Delete item from cart"""
        selected_item = self.cart_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Select an item from the cart to delete!")
            return
        
        # Get data from selected item
        item_values = self.cart_tree.item(selected_item[0], 'values')
        product_id = int(item_values[0])
        
        # Delete from cart
        self.cart = [item for item in self.cart if item['id'] != product_id]
        
        # Update display
        self.update_cart_display()
        self.calculate_total()

    def clear_cart(self):
        """Empty shopping cart"""
        if not self.cart:
            messagebox.showinfo("Info", "Cart is already empty!")
            return
        
        if messagebox.askyesno("Confirmation", "Are you sure you want to empty the cart?"):
            self.cart = []
            self.update_cart_display()
            self.calculate_total()

    def update_cart_display(self):
        """Update shopping cart display"""
        # Clear cart table
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        # Insert cart data
        for item in self.cart:
            price = int(item['price'])
            formatted_price = f"Rp {price:,.0f}".replace(",", ".")
            
            self.cart_tree.insert("", tk.END, values=(
                str(item['id']).zfill(3),
                item['name'],
                formatted_price,
                item['quantity']
            ))

    def calculate_total(self):
        """Calculate total purchase price"""
        total = 0
        for item in self.cart:
            total += item['price'] * item['quantity']
        
        # Format total
        formatted_total = f"Rp {total:,.0f}".replace(",", ".")
        self.total_label.config(text=f"Total: {formatted_total}")
        
        # Update status
        item_count = sum(item['quantity'] for item in self.cart)
        self.status_label.config(text=f" Cart: {len(self.cart)} product types, {item_count} items total")

    def checkout(self):
        """Process payment and reset cart"""
        if not self.cart:
            messagebox.showwarning("Warning", "Shopping cart is empty!")
            return
        
        # Calculate total
        total = sum(item['price'] * item['quantity'] for item in self.cart)
        formatted_total = f"Rp {total:,.0f}".replace(",", ".")
        
        # Display purchase summary
        summary = "=== PURCHASE SUMMARY ===\n\n"
        for item in self.cart:
            subtotal = item['price'] * item['quantity']
            formatted_subtotal = f"Rp {subtotal:,.0f}".replace(",", ".")
            summary += f"{item['name']} (x{item['quantity']}) - {formatted_subtotal}\n"
        
        summary += f"\nTOTAL PAYMENT: {formatted_total}"
        
        messagebox.showinfo("Payment Successful", summary)
        
        # Reset cart
        self.cart = []
        self.update_cart_display()
        self.calculate_total()
        self.id_var.set("")
        self.id_entry.focus()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductFinderApp(root)
    root.mainloop()