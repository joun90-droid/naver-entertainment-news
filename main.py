import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import tkinter as tk
from app_gui import NaverEntertainApp

def main():
    root = tk.Tk()
    app = NaverEntertainApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
