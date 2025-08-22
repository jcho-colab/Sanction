import os
import PyInstaller.__main__

def build_executable():
    PyInstaller.__main__.run([
        'src/main.py',
        '--onefile',           # Single executable
        '--windowed',          # No console window
        '--name=TableManager', # Executable name
        '--add-data=data:data', # Include data directory
        '--hidden-import=streamlit',
        '--hidden-import=streamlit.web.cli',
        '--hidden-import=streamlit.runtime.scriptrunner.script_runner',
        '--hidden-import=streamlit.runtime.state',
        '--hidden-import=streamlit.web.server.server',
        '--hidden-import=streamlit.components.v1',
        '--hidden-import=pandas',
        '--hidden-import=openpyxl',
        '--hidden-import=numpy',
        '--hidden-import=importlib.metadata',
        '--collect-all=streamlit',
        '--collect-all=altair',
        '--collect-all=plotly',
        '--collect-all=click',
        '--collect-all=tornado',
        '--collect-all=watchdog',
        '--collect-all=validators',
        '--collect-all=packaging',
        '--collect-all=importlib_metadata'
    ])

if __name__ == "__main__":
    build_executable()