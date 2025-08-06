import tkinter as tk
from gui import MainGUI
from config import config



if __name__ == "__main__":
    root = tk.Tk()
    MainGUI(root, config)
    root.mainloop() 

