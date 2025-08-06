import pyttsx3


class TTSVoice:
    def __init__(self, rate: int, volume: float) -> None:
        """Start the TTS engine, and set the volume and rate parameters"""
        self.rate = rate
        self.volume = volume

    def talk(self, text: str) -> None:
        """Run TTS engine for the given text"""
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", self.rate)
        self.engine.setProperty("volume", self.volume)
        self.engine.say(text)
        self.engine.runAndWait()
        del self.engine
