# Data Table Application

A Streamlit application for managing and manipulating CSV/Excel data tables.

## Features

- Load CSV and Excel files
- Sort data by columns
- Filter data by column values
- Aggregate data (sum, mean, count)
- Save processed data

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the application:

streamlit run src/main.py
```

## Building Executable

To build a standalone executable:
```
python build_exe.py
```

## Project Structure

```
├── src/
│   ├── __init__.py
│   ├── main.py                 # Main Streamlit application
│   ├── data_handler.py         # CSV/Excel data management
│   └── table_operations.py     # Advanced table manipulation
│
├── data/                       # Initial CSV storage
│   ├── table1.csv
│   ├── table2.csv
│   └── table3.csv
│
├── requirements.txt            # Project dependencies
├── build_exe.py                # PyInstaller configuration
└── README.md
```

## Dependencies

- streamlit
- pandas
- openpyxl
- pyinstaller