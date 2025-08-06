from typing import Any
from json_repair import repair_json
import requests
import json


class GemmaAPI:
    def __init__(self, config: dict[str, Any]) -> None:
        self.OLLAMA_GENERATE_ENDPOINT = config["ollama_settings"].get("generate_endpoint", "http://127.0.0.1:11434/api/generate")
        self.OLLAMA_CHAT_ENDPOINT = config["ollama_settings"].get("chat_endpoint", "http://127.0.0.1:11434/api/chat")

        self.model = None


    def _send_request(self, params: dict, endpoint_type: str="generate") -> Any:
        """Sending a request to the ollama server for the selected endpoint type"""
        assert endpoint_type in ["generate", "chat"], "Unknown 'endpoint_type' - _send_request(...)"

        selected_endpoint = ""
        match endpoint_type:
            case "generate":
                selected_endpoint = self.OLLAMA_GENERATE_ENDPOINT
            case "chat":
                selected_endpoint = self.OLLAMA_CHAT_ENDPOINT

        response = requests.post(
            url=selected_endpoint,
            headers={"Content-Type" : "application/json"},
            json=params
        )
        if not response.ok:
            raise Exception(f"Unable to set a request to Ollama - _send_request(...) - {response.status_code} - {response.content}")
        
        return response.json()


    def _format_json_output(self, text_json: str) -> Any:
        """Format model response with json in inside"""
        return json.loads(repair_json(text_json[text_json.find("{") : text_json.rfind("}") + 1])) 


    def load_model(self, model: str) -> None | bool:
        """Loading the selected model from Ollama"""

        if self._send_request({
            "model" : model,
            "prompt" : "",
            "keep_alive" : 30,
            "stream" : False
        }):
            self.model = model

            return True


    def generate_text(self, prompt: str, image: str="") -> tuple[Any, Any]:
        assert self.model, "First, select and load the model - load_model(...)"

        request_params = {
            "model" : self.model,
            "prompt" : prompt,
            "stream" : False
        }
        if image: request_params["images"] = [image]
        model_response = self._send_request(request_params, "generate")
        
        return model_response, self._format_json_output(model_response["response"])


    def generate_chat(self, messages: list) -> tuple[Any, Any, Any]:
        """Generation and handling of chat options by the model"""
        assert self.model, "First, select and load the model - load_model(...)"
        
        model_response = self._send_request({
            "model" : self.model,
            "messages" : messages,
            "stream" : False
        }, "chat")
        
        model_response_content = self._format_json_output(model_response["message"]["content"])
        model_response_message = model_response["message"]

        # Returns full response message to trace history and only formatted LLM json output 
        return model_response, model_response_message, model_response_content
