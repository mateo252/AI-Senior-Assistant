from .overlay import overlay_gui
from .voice import VoiceRecognitions
from .tts import TTSVoice
from screenshot import ScreenShot
import tkinter.font as tkFont
import tkinter as tk
import threading
import requests
import atexit



class AssistantGUI:
    def __init__(self, root: tk.Tk, config: dict, screenshot: ScreenShot) -> None:
        BUTTON_WIDTH = 100
        BUTTON_HEIGHT = 100

        self.config = config
        self.voice = VoiceRecognitions(model_path=self.config["voice_settings"]["vosk_model"])
        self.tts = TTSVoice(
            rate=self.config["tts_settings"]["rate"], 
            volume=self.config["tts_settings"]["volume"]
        )
        self.screenshot = screenshot

        self.is_dragging = False
        self.is_working = False
        self.stop = False
        
        self.bg_assistant_normal = self.config["colors_settings"]["bg_assistant_normal"]
        self.bg_assistant_click = self.config["colors_settings"]["bg_assistant_click"]
        self.bg_assistant_active = self.config["colors_settings"]["bg_assistant_active"]
        self.fg_assistant = self.config["colors_settings"]["fg_assistant"]

        self.root = root
        self.assistant_window = tk.Toplevel(self.root)
        self.assistant_window.resizable(False, False)
        self.assistant_window.overrideredirect(True)
        self.assistant_window.attributes("-topmost", True)

        screen_width = self.assistant_window.winfo_screenwidth()
        screen_height = self.assistant_window.winfo_screenheight()

        self.assistant_window.geometry(f"{BUTTON_WIDTH}x{BUTTON_HEIGHT}+{screen_width-200}+{screen_height-200}")
        
        atexit.register(self.voice.stop)
        self.run_assistant()


    def _run_assistant_thread(self) -> None:
        """Activate or deactivate the assistant"""
        self.is_working = True
        self.stop = False

        full_message_history = []
        while True:
            if (text := self.voice.listen_and_transcript()):
                
                screenshot_b64 = self.screenshot.take("llm")
                response = requests.post(
                    url="http://127.0.0.1:5000/desktop/audio",
                    headers={"Content-Type" : "application/json"},
                    json={
                        "user_message" : text,
                        "full_message_history" : full_message_history,
                        "image" : screenshot_b64
                    }
                )

                response_json = response.json()
                full_message_history = response_json["full_message_history"]

                if self.config["prompts_settings"]["overlay"]:
                    overlay_gui(self.root, response_json["content"]["hint"])

                self.tts.talk(response_json["content"]["assistant_message"])
                if response_json["content"]["is_running"] == "stop": 
                    break

            if self.stop == True:
                break
        
        self.assistant_button.config(bg=self.bg_assistant_normal)
        self.is_working = False
        self.stop = False


    def run_assistant(self) -> None:
        """Preparing the window and its functions to support the assistant"""
        def start_move(event) -> None:
            self.is_dragging = False
            self.assistant_window.x = event.x   # type: ignore
            self.assistant_window.y = event.y   # type: ignore

        def on_motion(event) -> None:
            self.is_dragging = True
            x = event.x_root - self.assistant_window.x  # type: ignore
            y = event.y_root - self.assistant_window.y  # type: ignore
            self.assistant_window.geometry(f"+{x}+{y}")

        def on_release(event) -> None:
            if not self.is_dragging:
                if not self.is_working:
                    self.is_working = True
                    self.assistant_button.config(bg=self.bg_assistant_active)
                    threading.Thread(target=self._run_assistant_thread, daemon=True).start()
                
                else:
                    self.assistant_button.config(bg=self.bg_assistant_normal)
                    self.stop = True
                    
            self.is_dragging = False


        self.assistant_button = tk.Button(
            master=self.assistant_window,
            text="AI",
            bg=self.bg_assistant_normal,
            fg=self.fg_assistant,
            activebackground=self.bg_assistant_click,
            bd=0,
            font=tkFont.Font(family="Segoe UI Emoji", size=40),
            cursor="hand2"
        )
        self.assistant_button.pack(fill="both", expand=True)

        self.assistant_button.bind("<Button-1>", start_move)
        self.assistant_button.bind("<B1-Motion>", on_motion)
        self.assistant_button.bind("<ButtonRelease-1>", on_release)
