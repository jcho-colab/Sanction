import os
import PyInstaller.__main__

def build_executable():
    PyInstaller.__main__.run([
        'main.py',
        '--onefile',           # Single executable
        '--windowed',          # No console window
        '--name=TableManager', # Executable name
        '--add-data=data:data' # Include data directory
    ])

if __name__ == "__main__":
    build_executable()