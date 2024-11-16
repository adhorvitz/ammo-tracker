import csv
import tkinter as tk
from tkinter import filedialog

def extract_data(csv_file):
    """
    Extracts ammunition data from a CSV file.

    Args:
      csv_file (str): The path to the CSV file.

    Returns:
      list: A list of dictionaries, where each dictionary represents an
            ammunition entry.
    """
    ammo_list = []
    try:
        with open(csv_file, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Convert quantities to integers
                row['quantity boxed'] = int(row['quantity boxed'])
                row['quantity loose'] = int(row['quantity loose'])
                row['Quantity in Box'] = int(row['Quantity in Box'])
                ammo_list.append(row)
    except FileNotFoundError:
        print(f"Error: File '{csv_file}' not found.")
        return None
    return ammo_list

def display_inventory(ammo_data):
    """
    Displays the ammunition inventory in the GUI.
    """
    inventory_window = tk.Toplevel(window)
    inventory_window.title("Ammunition Inventory")

    text_area = tk.Text(inventory_window)
    text_area.pack()

    output_string = ""
    for i, entry in enumerate(ammo_data):
        output_string += f"Entry {i+1}:\n"
        for key, value in entry.items():
            output_string += f"{key.strip()}: {value}\n"
        output_string += "\n"

    text_area.insert(tk.END, output_string)

def browse_file():
    """Opens a file dialog to select a CSV file."""
    file_path = filedialog.askopenfilename(
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )
    if file_path:
        ammo_data = extract_data(file_path)
        if ammo_data:
            # Enable the "Display Inventory" button
            display_button.config(state=tk.NORMAL)

            # Update the command of the "Display Inventory" button to use the current ammo_data
            display_button.config(command=lambda: display_inventory(ammo_data))

if __name__ == "__main__":
    window = tk.Tk()
    window.title("Ammo Tracker")

    browse_button = tk.Button(window, text="Browse CSV File", command=browse_file)
    browse_button.pack()

    display_button = tk.Button(window, text="Display Inventory", command=display_inventory, state=tk.DISABLED)
    display_button.pack()

    window.mainloop()