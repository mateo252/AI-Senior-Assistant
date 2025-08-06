# ✨ AI-Senior-Assistant
This project was created as part of the implementation of the competition task on the 🔗[Kaggle](https://www.kaggle.com/competitions/google-gemma-3n-hackathon) platform.
The task was to leverage the unique capabilities of Gemma3n to create a product that addresses a significant real-world challenge.

The prepared solution presents the use of Gemma3n as an intelligent assistant whose purpose is to protect and navigate seniors in the online environment and during daily computer use. This should contribute to increasing the independence and self-confidence of seniors when using new technological solutions.

## Setup
Download a repository
```
> git clone https://github.com/mateo252/AI-Senior-Assistant.git

> cd AI-Senior-Assistant
```

Create a virtual environment and install requirements
```
> python -m venv venv

> venv\Scripts\activate

(venv) > pip install -r requirements.txt

(venv) > cd src
```

From the [Vosk](https://alphacephei.com/vosk/models) website, download the model appropriate for your language.<br>
Unzip the downloaded files into the `/src` folder.

Before running the application, check and set the variables in the configuration file.<br>
The configuration file is located in `/config/config.json` and pay attention to:

- **vosk model** - you need to specify the name of the vosk model folder into which it was extracted
```json
"voice_settings" : {
    "vosk_model" : "..."
},
```

- **user settings** - settings for the user, which the application uses during operation
```json
"user_settings" : {
    "language" : "en",
    "level" : "beginner",
    "model" : "gemma3n:e4b-it-q4_K_M"
}
```

Key `user_settings.language` must match the key in `prompts_settings.language`.<br>
The purpose of this field is to tell the model what language you want its response to be in, e.g.
```json
"prompts_settings" : {
    "language" : {
        "esp" : "..."
    }
}
```
The same applies to the key `prompts_settings.user_level`. You can add a new one or change the name.

Other settigns:
- `ollama_settings` - allows to change the constant variables for ollama used in the application. At the moment the default settings are used,
- `prompts_settings.overlay` - (true/false) enable/disable function for the application (pointer to elemente by model). For the moment **deactivated**,
- `history_settings.run` - (true/false) setting the possibility of collecting user activity to the database,
- `screenshot_settings.interval` - screnshot interval in seconds,
- `screenshot_settings.screen` - screen number (all -1),

Methods of starting the application
```
(venv) > py main.py             // if you want to run assistant

(venv) > streamlit run stats.py // if you want to run stats
```

## License 
Apache 2.0