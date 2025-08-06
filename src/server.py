from flask import Flask, render_template, request, jsonify
from llm_ollama import GemmaAPI
from history import History
from config import config
import textwrap
import platform
import locale
import getpass
import base64
import os



app = Flask(__name__)
app_history = History() 

gemma = None
current_url = ""


@app.route("/status", methods=["GET"])
def status():
    """Check if the server is working"""
    return jsonify({"status" : "active"})


@app.route("/browser/activity", methods=["POST"])
def browser_activity():
    """This endpoint manage comunicats about user activity in browser"""
    global current_url
    global gemma
    task_prompt = None

    if request.method == "POST":
        if data := request.get_json(silent=True) or {}:
            match data.get("action"):
                case "websiteUrl":
                    if current_url != data.get("baseUrl"):
                        current_url = data.get("baseUrl")

                        task_prompt = \
                            config["prompts_settings"]["browser"]["website_url"].format(
                                clicked=data["clicked"],
                                link=data["link"],
                                website_title=data["websiteTitle"],
                                website_description=data["websiteDescription"],
                                base_url=data["baseUrl"],
                                full_url=data["fullUrl"]
                            )

                case "websitePermissionChange":
                    task_prompt = \
                        config["prompts_settings"]["browser"]["website_permission_change"].format(
                            permission=data["permission"],
                            website_title=data["websiteTitle"],
                            website_description=data["websiteDescription"],
                            base_url=data["baseUrl"],
                            full_url=data["fullUrl"]
                        )

                case "downloadStart":
                    pass

                case "downloadEnd":
                    task_prompt = \
                        config["prompts_settings"]["browser"]["download_end"].format(
                            is_safe=data["isSafe"],
                            file_name=data["fileName"],
                            referrer=data["referrer"],
                            url=data["url"]
                        )
                    
            if task_prompt:
                model_prompt = \
                    f"""
                    {config['prompts_settings']['browser']['core']}\n
                    {config['prompts_settings']['user_level'][config['user_settings']['level']]}\n
                    {task_prompt}\n
                    {config['prompts_settings']['language'][config['user_settings']['language']]}
                    """

                # - 'full_model_response' - full response from Ollama server 
                # - 'model_response_json' - formatted only the content of the model's answer
                full_model_response, model_response_json = gemma.generate_text(              # type: ignore
                    prompt=textwrap.dedent(model_prompt).strip()
                ) 
                print(model_response_json)
                # If 'true' history will be save in DB
                if config["history_settings"]["run"]:
                    full_model_response.update({
                        "type" : "text",
                        "user_prompt" : model_prompt
                    })
                    app_history.save_to_sqlite(full_model_response)

                return jsonify({
                    "action" : model_response_json["action"],
                    "message" : render_template(
                        template_name_or_list="notification.html",
                        title=model_response_json["type"].capitalize(),
                        message=model_response_json["message"]
                    )
                })
            
    return jsonify({})


@app.route("/desktop/audio", methods=["POST"])
def desktop_audio():
    """This endpoint manages the communication between the user and the assistant"""
    global gemma
    if request.method == "POST":
        if data := request.get_json(silent=True) or {}:

            # Add a system prompt if it is the beginning of the chat
            if not data["full_message_history"]:
                data["full_message_history"].append({
                    "role" : "system",
                    "content" : \
                    f"""
                    {config['prompts_settings']['desktop']['core']}\n
                    {config['prompts_settings']['user_level'][config['user_settings']['level']]}\n
                    {config['prompts_settings']['desktop']['task'].format(
                        os_name=platform.uname().system,
                        os_version=platform.uname().release,
                        system_language=locale.getdefaultlocale()[0],
                        current_user=getpass.getuser()
                    )}\n
                    {config['prompts_settings']['language'][config['user_settings']['language']]}\n
                    """ 
                })

            # Add content to the history that the user uploaded
            data["full_message_history"].append({
                "role" : "user",
                "content" : data["user_message"],
                "images" : [data["image"]]
            })

            # Generating model response to user content when it knows the whole history
            # - 'full_model_response' - full response from Ollama server 
            # - 'llm_response_message' - whole model response structure
            # - 'llm_response_content' - formatted only the content of the model's answer
            full_model_response, llm_response_message, llm_response_content = gemma.generate_chat(data["full_message_history"])  # type: ignore
            data["full_message_history"].append(llm_response_message)

            # History structure
            # - 'system'
            # - 'user'
            # - 'assistant'

            if config["history_settings"]["run"]:
                full_model_response.update({
                    "type" : "chat",
                    "user_prompt" : data["user_message"]
                })
                app_history.save_to_sqlite(full_model_response)

            return jsonify({
                "content" : llm_response_content,
                "full_message_history" : data["full_message_history"]
            })

    return jsonify({})


@app.route("/desktop/screenshot", methods=["POST"])
def desktop_screenshot():
    global gemma
    if request.method == "POST":
        if data := request.get_json(silent=True) or {}:
            with open(data["img_path"], "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("utf-8")

            full_model_response, llm_model_img_response = gemma.generate_text(      # type: ignore
                prompt=config["prompts_settings"]["desktop"]["image"],
                image=img_b64
            )

            img_description = llm_model_img_response["description"]
            img_tag = llm_model_img_response["tag"]
            img_metadata = {
                "created_at" : data["created_at"],
                "img_path" : data["img_path"],
                "filename" : os.path.basename(data["img_path"]),
                "tag" : img_tag
            }

            if config["history_settings"]["run"]:
                full_model_response.update({
                    "type" : "image",
                    "user_prompt" : config["prompts_settings"]["desktop"]["image"]
                })
                app_history.save_to_sqlite(full_model_response)
                app_history.save_to_chroma(img_description, img_metadata)

        
    return jsonify({})


def run_server() -> None:
    """Load the ollama model and start the Flask server"""
    global gemma
    gemma = GemmaAPI(config)
    gemma.load_model(config["user_settings"]["model"])
    
    app.run(host="127.0.0.1", port=5000, debug=False)