Ammo Tracker
        This project is a Python-based application for tracking ammunition inventory. It provides a simple and efficient way to manage and organize your ammo collection.

Features
        Read Data: Import ammo data from a CSV file.
        Inventory Display: View your ammo inventory in a user-friendly format.
        Add Entries: Add new ammo records.
        Update Records: Edit existing entries to reflect changes in your inventory.
        Delete Entries: Remove records with a confirmation prompt.
        Search: Search for specific ammo records using advanced filters.
        Backup & Restore: Safeguard your data by backing up the SQLite database and restoring it when needed.
        Data Visualization: Display inventory statistics with bar charts using matplotlib.
        Audit Logging: Track all add, edit, and delete actions in a detailed log file.

Getting Started

        Clone the Repository:
                git clone https://github.com/adhorvitz/ammo-tracker.git
        
        Set Up Environment (Optional):
                python -m venv .venv
                source .venv/bin/activate  # Linux/MacOS
                .\.venv\Scripts\activate   # Windows
        
        
        Install Dependencies:
                pip install matplotlib python-dateutil
        
        Run the Application:
                python ammo_tracker.py

Current Development: adhorvitz-feature/functions-and-enhancements

        This branch focuses on expanding the functionality of the Ammo Tracker application. Updates include:
        
                Dynamic Inventory Refresh: Automatically refreshes the displayed inventory after every action (e.g., add, edit, delete).
                Database Backup & Restore: Allows users to back up their SQLite database to a chosen location and restore it when needed.
                Enhanced Search Functionality: Supports advanced multi-criteria filtering, including filtering by ammo type, brand, gauge/size, and date range.
                Data Visualization: Provides bar charts summarizing inventory data by ammo type using matplotlib.
                Audit Logging: Logs all actions (add, edit, delete) to a text-based audit log (audit_log.txt) for tracking changes.
                Development Progress
                Features Added in This Branch
                Dynamic Inventory Refresh: Ensures displayed inventory reflects the latest changes.
                Backup and Restore: Adds functionality to safeguard and recover data.
                Advanced Search Options: Enables multi-criteria filtering.
                Data Visualization: Generates bar charts for better data analysis.
                Audit Logging: Tracks user actions for accountability.
                Planned Features
                Implement sorting for displayed inventory columns.
                Add user authentication for multi-user environments.
                Include price tracking and additional analytics.
        
        Known Issues
                None identified in the current development phase.

Contributing
        Contributions are welcome! Please feel free to open an issue or submit a pull request.

License
        This project is licensed under the MIT License.
