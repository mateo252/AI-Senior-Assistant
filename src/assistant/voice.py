from vosk import Model, KaldiRecognizer
import pyaudio
import json


class VoiceRecognitions:
    def __init__(
        self,
        model_path: str="vosk-model-en-us-0.22-lgraph",
        sample_rate=16_000,
        chunk: int=4096
    ) -> None:
        
        self.sample_rate = sample_rate
        self.chunk = chunk

        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, sample_rate)

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sample_rate,
            input=True,
            frames_per_buffer=8192
        )
        self.stream.start_stream()


    def stop(self) -> None:
        """Close all open streams"""
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()


    def listen_and_transcript(self) -> str | None:
        """Read audio data stream"""
        data = self.stream.read(num_frames=self.chunk, exception_on_overflow=False)
        if self.recognizer.AcceptWaveform(data):

            result = json.loads(self.recognizer.Result())
            if text := result.get("text", "").strip():
                return text
            
            return None