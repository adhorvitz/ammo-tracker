# Ammo Tracker

This project is a Python-based application for tracking ammunition inventory. It provides a simple way to manage and organize your ammo collection.

## Features

*   Read ammo data from a CSV file.
*   Display inventory in a user-friendly format.
*   Add new ammo entries.
*   Update existing entries (e.g., when ammo is used).
*   Remove ammo entries.
*   Search for specific ammo types.
*   (Planned) Track dates and prices.
*   (Planned) Graphical User Interface (GUI) for easier interaction.

## Getting Started

1.  Clone the repository: `git clone https://github.com/adhorvitz/ammo-tracker.git`
2.  (Optional) Set up a virtual environment: `python -m venv .venv`
3.  Install dependencies: (We'll add any necessary libraries here later)
4.  Run the script: `python ammo_tracker.py`

## Development Progress

- **Current Branch**: `adhorvitz-feature/delete-and-enhancements`
- **Status**: In Progress
  - Added delete functionality with confirmation prompts.
  - Improved error handling for editing and deleting records.
  - Validated input fields, including date formats and numeric values.
- **Next Steps**:
  - Expand search functionality to support multiple filters and date ranges.
  - Add a backup/restore option for the SQLite database.
  - Perform final testing and prepare for merge into `main` branch.

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

## License
MIT License
