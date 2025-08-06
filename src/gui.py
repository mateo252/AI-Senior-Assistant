import tkinter as tk
from tkinter.font import Font
from server import run_server
from screenshot import ScreenShot
from assistant.assistant import AssistantGUI
import subprocess
import threading
import requests
import time
import sys
import os



class MainGUI:
    def __init__(self, root: tk.Tk, config: dict) -> None:
        self.root = root
        self.root.title("AI-Senior-Assistant")

        WINDOW_WIDTH = 400
        WINDOW_HEIGHT = 210
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{screen_width//2 - WINDOW_WIDTH}+{screen_height//2 - WINDOW_HEIGHT}")
        
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.config = config
        self.process_ollama = None

        self.bg_accept_color = self.config["colors_settings"]["bg_accept_status"]
        self.bg_error_color = self.config["colors_settings"]["bg_error_status"]

        os.makedirs(os.path.join(
            os.path.dirname(os.path.abspath(sys.argv[0])),
            "hsitory"
        ), exist_ok=True)
        self.screenshot = ScreenShot(self.config)

        self.main_menu()
    

    def _run_servers(self) -> None:
        """Checking and starting Ollama and Flask server"""
        server_error = False
        server_button_text = "Servers are running ✅"

        self.process_ollama = subprocess.Popen(["ollama", "serve"])
        try:
            response = requests.get(url=self.config["ollama_settings"].get("address", "http://127.0.0.1:11434/")) # Default if not in config
            if not response.ok:
                server_error = True
                server_button_text = "Ollama server issue ❌"

        except requests.ConnectionError:
            server_error = True
            server_button_text = "Ollama server is not working ❌"

        if not server_error:
            threading.Thread(target=run_server, daemon=True).start()
            
            try:
                time.sleep(5)
                response = requests.get("http://127.0.0.1:5000/status") # Static
                if not response.ok:
                    print(response.ok)
                    server_error = True
                    server_button_text = "Web server issue ❌"

            except requests.ConnectionError:
                server_error = True
                server_button_text = "Web server is not working ❌"
        
        if server_error:
            self.server_btn.config(text=server_button_text, state="disabled", bg=self.bg_error_color)

        else:
            if self.config["history_settings"]["run"]:
                threading.Thread(target=self.screenshot.save_history, daemon=True).start()

            self.server_btn.config(text=server_button_text, state="disabled", bg=self.bg_accept_color)
            self.assistant_btn.config(state="normal")


    def _run_assistant(self) -> None:
        """Launch AI assistant"""
        assistant_button_text = "Assistant is running ✅"
        self.assistant_btn.config(text=assistant_button_text, state="disabled", bg=self.bg_accept_color)
        AssistantGUI(self.root, self.config, self.screenshot)


    def _on_close(self) -> None:
        """Termination of subprocesses after shutdown"""
        if self.process_ollama is not None:
            if self.process_ollama.poll() is None:
                self.process_ollama.kill()
                self.process_ollama.wait()
                os.system("taskkill /IM ollama.exe /F") # Windows

        try:
            self.root.destroy()
        except Exception:
            pass


    def main_menu(self) -> None:
        """Two main buttons to run Flask server and assistant"""
        self.server_btn = tk.Button(
            self.root,
            text="Start servers",
            font=Font(family="Segoe UI Emoji", size=10, weight="bold"),
            cursor="hand2",
            command=self._run_servers
        )
        self.server_btn.pack(anchor="center", fill="both", ipady=25, padx=15, pady=15)

        self.assistant_btn = tk.Button(
            self.root,
            text="Start assistant",
            font=Font(family="Segoe UI Emoji", size=10, weight="bold"),
            cursor="hand2",
            state="disabled",
            command=self._run_assistant
        )
        self.assistant_btn.pack(anchor="center", fill="both", ipady=25, padx=15)        
