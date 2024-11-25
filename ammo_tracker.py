import csv
import sqlite3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


# ---------------------------------------------------------------------------------
# DATABASE FUNCTIONS: Handle SQLite database creation and population.
# ---------------------------------------------------------------------------------

def create_database(db_file="ammo.db"):
    """
    Creates the SQLite database schema. Drops the existing `ammo` table
    if it exists to ensure the schema matches the corrected CSV structure.
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Drop the table if it exists
    cursor.execute("DROP TABLE IF EXISTS ammo")

    # Create the table with the corrected schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ammo (
            Ammo_Type TEXT,
            Gauge_or_Ammo_Size TEXT,
            Brand TEXT,
            Slug_Size TEXT,
            Quantity_Box INTEGER,
            Quantity_Loose INTEGER,
            Quantity_in_Magazine INTEGER,
            Type TEXT,
            Grain TEXT,
            Firearm_Type TEXT,
            Date_Entered TEXT
        )
    """)
    conn.commit()
    conn.close()


def populate_database_from_csv(csv_file, db_file="ammo.db"):
    """
    Populates the SQLite database with data from a CSV file.
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    with open(csv_file, 'r', newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)

        # Normalize headers
        reader.fieldnames = [header.strip().replace(" ", "_") for header in reader.fieldnames]

        for row in reader:
            cursor.execute("""
                INSERT INTO ammo (Ammo_Type, Gauge_or_Ammo_Size, Brand, Slug_Size, Quantity_Box,
                                  Quantity_Loose, Quantity_in_Magazine, Type, Grain, Firearm_Type, Date_Entered)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row.get('Ammo_Type', ''),
                row.get('Gauge_or_Ammo_Size', ''),
                row.get('Brand', ''),
                row.get('Slug_Size', ''),
                int(row.get('Quantity_Box', 0)),
                int(row.get('Quantity_Loose', 0)),
                int(row.get('Quantity_in_Magazine', 0)),
                row.get('Type', ''),
                row.get('Grain', ''),
                row.get('Firearm_Type', ''),
                row.get('Date_Entered', '')
            ))

    conn.commit()
    conn.close()


def extract_data(db_file="ammo.db"):
    """
    Fetches all rows from the database.
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT rowid, * FROM ammo")
    rows = cursor.fetchall()
    conn.close()

    keys = ["ID", "Ammo_Type", "Gauge_or_Ammo_Size", "Brand", "Slug_Size", "Quantity_Box",
            "Quantity_Loose", "Quantity_in_Magazine", "Type", "Grain", "Firearm_Type", "Date_Entered"]
    return [dict(zip(keys, row)) for row in rows]


# ---------------------------------------------------------------------------------
# GUI FUNCTIONS: Handle user interactions and display components.
# ---------------------------------------------------------------------------------

def display_inventory():
    """
    Displays the inventory in a new window with tabular view.
    """
    inventory_window = tk.Toplevel(window)
    inventory_window.title("Ammunition Inventory")

    tree = ttk.Treeview(inventory_window, columns=(
        "ID", "Ammo_Type", "Gauge_or_Ammo_Size", "Brand", "Slug_Size", "Quantity_Box",
        "Quantity_Loose", "Quantity_in_Magazine", "Type", "Grain", "Firearm_Type", "Date_Entered"
    ), show="headings")

    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")

    for entry in extract_data():
        tree.insert("", "end", values=tuple(entry.values()))

    tree.pack(fill="both", expand=True)

    def export_to_csv():
        """
        Exports the displayed inventory to a CSV file.
        """
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            with open(file_path, "w", newline='', encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=tree["columns"])
                writer.writeheader()
                writer.writerows(extract_data())
            messagebox.showinfo("Export Successful", f"Inventory exported to {file_path}.")

    export_button = tk.Button(inventory_window, text="Export to CSV", command=export_to_csv)
    export_button.pack(pady=10)


def load_initial_csv():
    """
    Loads the initial CSV file to populate the database.
    """
    file_path = filedialog.askopenfilename(
        title="Select CSV File",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )
    if file_path:
        try:
            populate_database_from_csv(file_path)
            messagebox.showinfo("Success", "Database loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {e}")


def add_inventory():
    """
    Adds a new inventory item via a form.
    """
    def save_inventory():
        try:
            new_entry = {
                'Ammo_Type': ammo_type_entry.get(),
                'Gauge_or_Ammo_Size': gauge_entry.get(),
                'Brand': brand_entry.get(),
                'Slug_Size': slug_entry.get(),
                'Quantity_Box': int(box_entry.get()),
                'Quantity_Loose': int(loose_entry.get()),
                'Quantity_in_Magazine': int(mag_entry.get()),
                'Type': type_entry.get(),
                'Grain': grain_entry.get(),
                'Firearm_Type': firearm_entry.get(),
                'Date_Entered': date_entry.get()
            }

            conn = sqlite3.connect("ammo.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ammo (Ammo_Type, Gauge_or_Ammo_Size, Brand, Slug_Size, Quantity_Box,
                                  Quantity_Loose, Quantity_in_Magazine, Type, Grain, Firearm_Type, Date_Entered)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(new_entry.values()))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Inventory added successfully!")
            add_window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid data entry. Check quantities.")

    add_window = tk.Toplevel(window)
    add_window.title("Add Inventory")

    labels = ["Ammo Type", "Gauge or Ammo Size", "Brand", "Slug Size", "Quantity Box",
              "Quantity Loose", "Quantity in Magazine", "Type", "Grain", "Firearm Type", "Date Entered"]
    entries = {}

    for i, label in enumerate(labels):
        tk.Label(add_window, text=f"{label}:").grid(row=i, column=0, padx=5, pady=5)
        entries[label] = tk.Entry(add_window)
        entries[label].grid(row=i, column=1, padx=5, pady=5)

    ammo_type_entry = entries["Ammo Type"]
    gauge_entry = entries["Gauge or Ammo Size"]
    brand_entry = entries["Brand"]
    slug_entry = entries["Slug Size"]
    box_entry = entries["Quantity Box"]
    loose_entry = entries["Quantity Loose"]
    mag_entry = entries["Quantity in Magazine"]
    type_entry = entries["Type"]
    grain_entry = entries["Grain"]
    firearm_entry = entries["Firearm Type"]
    date_entry = entries["Date Entered"]

    tk.Button(add_window, text="Save", command=save_inventory).grid(row=len(labels), column=1, pady=10)


def search_inventory():
    """
    Allows the user to search the inventory based on a type filter.
    """
    search_window = tk.Toplevel(window)
    search_window.title("Search Inventory")

    tk.Label(search_window, text="Search by Type:").pack(pady=5)
    type_entry = tk.Entry(search_window)
    type_entry.pack(pady=5)

    def perform_search():
        search_term = type_entry.get().lower()
        results = [row for row in extract_data() if search_term in row["Type"].lower()]

        if not results:
            messagebox.showinfo("No Results", "No items match your search.")
            return

        results_window = tk.Toplevel(search_window)
        results_window.title("Search Results")

        tree = ttk.Treeview(results_window, columns=results[0].keys(), show="headings")
        for col in results[0].keys():
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")
        for row in results:
            tree.insert("", "end", values=tuple(row.values()))

        tree.pack(fill="both", expand=True)

    tk.Button(search_window, text="Search", command=perform_search).pack(pady=10)


# ---------------------------------------------------------------------------------
# MAIN PROGRAM: Initialize and run GUI.
# ---------------------------------------------------------------------------------

window = tk.Tk()
window.title("Ammo Tracker")

# Add primary buttons
tk.Button(window, text="Load Initial CSV", command=load_initial_csv).pack(pady=5)
tk.Button(window, text="Display Inventory", command=display_inventory).pack(pady=5)
tk.Button(window, text="Add Inventory", command=add_inventory).pack(pady=5)
tk.Button(window, text="Search Inventory", command=search_inventory).pack(pady=5)

# Ensure the database schema is created
create_database()

# Start the main GUI loop
window.mainloop()
