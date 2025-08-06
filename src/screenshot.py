from datetime import datetime, date
from mss import mss
import requests
import base64
import time
import sys
import os


class ScreenShot:
    def __init__(self, config: dict) -> None:
        self.config = config
        self.image_format = self.config["screenshot_settings"]["format"]
        self.monitor_id = self.config["screenshot_settings"]["screen"]

        main_file_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.tmp_screens_path = os.path.join(main_file_path, "history", "tmp")
        os.makedirs(self.tmp_screens_path, exist_ok=True)

        self.screens_path = os.path.join(main_file_path, "history", "ScreenShots", str(date.today()).replace("-", "_"))
        os.makedirs(self.screens_path, exist_ok=True)


    def take(self, img_type: str) -> str | None:
        """Screneshot depending on the 'img_type' selected"""
        assert img_type in ["llm", "history"], "Wrong 'img_type' - take(...)"

        full_save_path = (
            os.path.join(self.tmp_screens_path, f"tmp_screen.{self.image_format.lower()}")
            if img_type == "llm"
            else os.path.join(
                self.screens_path,
                f"screen_{len(os.listdir(self.screens_path)):05d}.{self.image_format.lower()}"
            )
        )

        with mss() as sct:
            sct.shot(mon=self.monitor_id, output=full_save_path)

        if img_type == "llm":
            with open(full_save_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
            
        elif img_type == "history":
            return full_save_path


    def save_history(self) -> None:
        """Sending screenshots to be stored in the chroma database"""
        while True:
            time.sleep(self.config["screenshot_settings"]["interval"])
            img_path = self.take("history")

            try:
                response = requests.post(
                    url="http://127.0.0.1:5000/desktop/screenshot",
                    headers={"Content-Type" : "application/json"},
                    json={
                        "img_path" : img_path,
                        "created_at" : datetime.now().isoformat(),
                    })
                
            except requests.RequestException:
                raise Exception("class ScreenShot - Server request error")

            if not response.ok:
                raise Exception(f"class ScreenShot - response not ok - status {response.status_code}")
            
