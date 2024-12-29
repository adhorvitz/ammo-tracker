import csv
import sqlite3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from dateutil import parser  # For flexible date parsing
import shutil
import matplotlib.pyplot as plt
import datetime


# ---------------------------------------------------------------------------------
# DATABASE FUNCTIONS: Handle SQLite database creation and population.
# ---------------------------------------------------------------------------------

def create_database(db_file="ammo.db"):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS ammo")
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
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    with open(csv_file, 'r', newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
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
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT rowid, * FROM ammo")
    rows = cursor.fetchall()
    conn.close()
    keys = ["ID", "Ammo_Type", "Gauge_or_Ammo_Size", "Brand", "Slug_Size", "Quantity_Box",
            "Quantity_Loose", "Quantity_in_Magazine", "Type", "Grain", "Firearm_Type", "Date_Entered"]
    return [dict(zip(keys, row)) for row in rows]

def backup_database():
    """
    Backs up the SQLite database to a user-specified location.
    """
    backup_path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("SQLite Database", "*.db")])
    if backup_path:
        try:
            shutil.copy("ammo.db", backup_path)
            messagebox.showinfo("Success", "Database backed up successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to back up database: {e}")

def restore_database():
    """
    Restores the SQLite database from a user-selected backup.
    """
    restore_path = filedialog.askopenfilename(filetypes=[("SQLite Database", "*.db")])
    if restore_path:
        try:
            shutil.copy(restore_path, "ammo.db")
            messagebox.showinfo("Success", "Database restored successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restore database: {e}")

# ---------------------------------------------------------------------------------
# HELPER FUNCTIONS: Validation, Refresh, and Update
# ---------------------------------------------------------------------------------

def validate_date(date_str):
    try:
        parsed_date = parser.parse(date_str)
        return parsed_date.strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD, MM/DD/YYYY, or MM-DD-YYYY.")


def refresh_inventory(tree):
    """
    Refreshes the inventory Treeview with updated data.
    """
    tree.delete(*tree.get_children())  # Clear existing rows
    for entry in extract_data():
        tree.insert("", "end", values=tuple(entry.values()))


def delete_record(tree):
    """
    Deletes the selected record from the database.
    """
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("No Selection", "Please select a record to delete.")
        return

    # Fetch the selected record's ID
    item_id = tree.item(selected_item)["values"][0]

    # Confirm deletion
    confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this record?")
    if not confirm:
        return

    try:
        # Delete the record from the database
        conn = sqlite3.connect("ammo.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ammo WHERE rowid = ?", (item_id,))
        conn.commit()
        conn.close()

        # Remove the record from the Treeview
        tree.delete(selected_item)
        refresh_inventory(tree)  # Auto-refreshes the displayed inventory
        # Log the action
        log_action("Delete", f"Deleted record with ID {item_id}")


        messagebox.showinfo("Success", "Record deleted successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete record: {e}")

def show_statistics():
    """
    Displays a bar chart summarizing inventory by Ammo Type.
    """
    conn = sqlite3.connect("ammo.db")
    cursor = conn.cursor()
    cursor.execute("SELECT Ammo_Type, SUM(Quantity_Box + Quantity_Loose) AS Total FROM ammo GROUP BY Ammo_Type")
    data = cursor.fetchall()
    conn.close()

    # Prepare data for the chart
    types = [row[0] for row in data]
    totals = [row[1] for row in data]

    plt.bar(types, totals)
    plt.xlabel("Ammo Type")
    plt.ylabel("Total Quantity")
    plt.title("Inventory by Ammo Type")
    plt.show()


# ---------------------------------------------------------------------------------
# GUI FUNCTIONS: Handle user interactions and display components.
# ---------------------------------------------------------------------------------

def load_initial_csv():
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


def display_inventory():
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


def add_inventory():
    def save_inventory():
        try:
            new_entry = {
                "Ammo_Type": ammo_type_entry.get(),
                "Gauge_or_Ammo_Size": gauge_entry.get(),
                "Brand": brand_entry.get(),
                "Slug_Size": slug_entry.get(),
                "Quantity_Box": int(box_entry.get()),
                "Quantity_Loose": int(loose_entry.get()),
                "Quantity_in_Magazine": int(mag_entry.get()),
                "Type": type_entry.get(),
                "Grain": grain_entry.get(),
                "Firearm_Type": firearm_entry.get(),
                "Date_Entered": validate_date(date_entry.get())
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
            log_action("Add", f"Added new inventory: {new_entry}")
        except ValueError as ve:
            messagebox.showerror("Validation Error", f"Invalid input: {ve}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")

    add_window = tk.Toplevel(window)
    add_window.title("Add Inventory")

    labels = ["Ammo Type", "Gauge or Ammo Size", "Brand", "Slug Size", "Quantity Box",
              "Quantity Loose", "Quantity in Magazine", "Type", "Grain", "Firearm Type", "Date Entered"]
    entries = {}
    for i, label in enumerate(labels):
        tk.Label(add_window, text=label).grid(row=i, column=0, padx=5, pady=5)
        entry = tk.Entry(add_window)
        entry.grid(row=i, column=1, padx=5, pady=5)
        entries[label.replace(" ", "_")] = entry

    ammo_type_entry = entries["Ammo_Type"]
    gauge_entry = entries["Gauge_or_Ammo_Size"]
    brand_entry = entries["Brand"]
    slug_entry = entries["Slug_Size"]
    box_entry = entries["Quantity_Box"]
    loose_entry = entries["Quantity_Loose"]
    mag_entry = entries["Quantity_in_Magazine"]
    type_entry = entries["Type"]
    grain_entry = entries["Grain"]
    firearm_entry = entries["Firearm_Type"]
    date_entry = entries["Date_Entered"]

    refresh_inventory(tree)  # Auto-refreshes the displayed inventory

    tk.Button(add_window, text="Save", command=save_inventory).grid(row=len(labels), column=1, pady=10)


def search_inventory():
    """
    Opens a form for advanced inventory search, including single-term search and multi-criteria search.
    """
    search_window = tk.Toplevel(window)
    search_window.title("Advanced Search")

    # Create input fields for multi-criteria search
    criteria = {}
    labels = ["Ammo Type", "Brand", "Gauge or Ammo Size", "Date (Start)", "Date (End)"]
    for i, label in enumerate(labels):
        tk.Label(search_window, text=f"{label}:").grid(row=i, column=0, padx=5, pady=5)
        entry = tk.Entry(search_window)
        entry.grid(row=i, column=1, padx=5, pady=5)
        criteria[label] = entry

    def perform_search():
        """
        Searches the database with multiple criteria and displays results.
        """
        query = "SELECT * FROM ammo WHERE 1=1"
        params = []

        # Build query dynamically
        if criteria["Ammo Type"].get():
            query += " AND Ammo_Type LIKE ?"
            params.append(f"%{criteria['Ammo Type'].get()}%")
        if criteria["Brand"].get():
            query += " AND Brand LIKE ?"
            params.append(f"%{criteria['Brand'].get()}%")
        if criteria["Gauge or Ammo Size"].get():
            query += " AND Gauge_or_Ammo_Size LIKE ?"
            params.append(f"%{criteria['Gauge or Ammo Size'].get()}%")
        if criteria["Date (Start)"].get() and criteria["Date (End)"].get():
            query += " AND Date_Entered BETWEEN ? AND ?"
            params.append(criteria["Date (Start)"].get())
            params.append(criteria["Date (End)"].get())

        # Execute query and fetch results
        conn = sqlite3.connect("ammo.db")
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        # Display results
        if not results:
            messagebox.showinfo("No Results", "No items match your search.")
            return

        results_window = tk.Toplevel(search_window)
        results_window.title("Search Results")
        columns = ["ID", "Ammo_Type", "Gauge_or_Ammo_Size", "Brand", "Slug_Size",
                   "Quantity_Box", "Quantity_Loose", "Quantity_in_Magazine", "Type",
                   "Grain", "Firearm_Type", "Date_Entered"]
        tree = ttk.Treeview(results_window, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")
        for row in results:
            tree.insert("", "end", values=row)
        tree.pack(fill="both", expand=True)

    # Add "Search" button
    tk.Button(search_window, text="Search", command=perform_search).grid(row=len(labels), column=1, pady=10)



def edit_inventory():
    """
    Displays inventory in a Treeview with options to edit or delete records.
    """
    inventory_window = tk.Toplevel(window)
    inventory_window.title("Edit Inventory")

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

    def open_edit_form():
        edit_record(tree)

    # Add buttons for Edit and Delete functionality
    edit_button = tk.Button(inventory_window, text="Edit Selected Record", command=open_edit_form)
    edit_button.pack(pady=5)

    delete_button = tk.Button(inventory_window, text="Delete Selected Record", command=lambda: delete_record(tree))
    delete_button.pack(pady=5)


def edit_record(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("No Selection", "Please select a record to edit.")
        return

    item_id = tree.item(selected_item)["values"][0]
    record = next(row for row in extract_data() if row["ID"] == item_id)

    edit_window = tk.Toplevel(window)
    edit_window.title("Edit Record")

    labels = ["Ammo Type", "Gauge or Ammo Size", "Brand", "Slug Size", "Quantity Box",
              "Quantity Loose", "Quantity in Magazine", "Type", "Grain", "Firearm Type", "Date Entered"]
    entries = {}
    for i, label in enumerate(labels):
        tk.Label(edit_window, text=label).grid(row=i, column=0, padx=5, pady=5)
        entry = tk.Entry(edit_window)
        entry.insert(0, record[label.replace(" ", "_")])
        entry.grid(row=i, column=1, padx=5, pady=5)
        entries[label.replace(" ", "_")] = entry

    refresh_inventory(tree)  # Auto-refreshes the displayed inventory

    def save_changes():
        """
        Saves changes to the database and refreshes the inventory display.
        """
        try:
            updated_record = {
                key: validate_date(entries[key].get()) if key == "Date_Entered" else
                int(entries[key].get()) if "Quantity" in key and entries[key].get() else 0
                if "Quantity" in key else
                entries[key].get()
                for key in entries
            }

            conn = sqlite3.connect("ammo.db")
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE ammo
                SET Ammo_Type = ?, Gauge_or_Ammo_Size = ?, Brand = ?, Slug_Size = ?, Quantity_Box = ?,
                    Quantity_Loose = ?, Quantity_in_Magazine = ?, Type = ?, Grain = ?, Firearm_Type = ?, Date_Entered = ?
                WHERE rowid = ?
            """, tuple(updated_record.values()) + (item_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Record updated successfully!")
            refresh_inventory(tree)
            edit_window.destroy()
            log_action("Edit", f"Edited record ID {item_id}")
        except ValueError as ve:
            messagebox.showerror("Validation Error", f"Error: {ve}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")

    tk.Button(edit_window, text="Save Changes", command=save_changes).grid(row=len(labels), column=1, pady=10)

def log_action(action, details):
    """
    Logs actions (add, edit, delete) to a text file.
    """
    with open("audit_log.txt", "a") as log_file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"{timestamp} | {action} | {details}\n")

# ---------------------------------------------------------------------------------
# MAIN PROGRAM: Initialize and run GUI.
# ---------------------------------------------------------------------------------

window = tk.Tk()
window.title("Ammo Tracker")

# Add primary buttons
tk.Button(window, text="Load Initial CSV", command=load_initial_csv).pack(pady=5)
tk.Button(window, text="Display Inventory", command=display_inventory).pack(pady=5)
tk.Button(window, text="Add Inventory", command=add_inventory).pack(pady=5)
tk.Button(window, text="Edit Inventory", command=edit_inventory).pack(pady=5)
tk.Button(window, text="Backup Database", command=backup_database).pack(pady=5)
tk.Button(window, text="Restore Database", command=restore_database).pack(pady=5)
tk.Button(window, text="Show Statistics", command=show_statistics).pack(pady=5)
tk.Button(window, text="Search Inventory", command=search_inventory).pack(pady=5)


# Ensure the database schema is created
create_database()

# Start the main GUI loop
print("Starting the Ammo Tracker application...")
window.mainloop()
print("Program has exited.")
