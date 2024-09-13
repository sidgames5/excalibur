# Excalibur

A simple voice assistant that respects your privacy. All voice assistants and smart speakers use proprietary systems and are spying on us 24/7. The goal of this project is to replace all of the spyware voice assistants in your digital life.

## Features

🟥 Confirmed not working yet

🟨 Partially working/in development

🟩 Fully working

🟦 Needs testing

⬛ Not implemented

| Feature | Windows | MacOS | Linux |
|-|-|-|-|
| Speech recognition | 🟦 | 🟦 | 🟩 |
| Text to speech | 🟦 | 🟦 | 🟩 |
| Basic questions | 🟦 | 🟩 | 🟩 |
| Advanced questions* | 🟦 | 🟦 | 🟩 |
| Time | 🟦 | 🟩 | 🟩 |
| Weather | 🟦 | 🟩 | 🟩 |
| Smart device control | ⬛ | ⬛ | 🟨 |
| Music control | ⬛ | ⬛ | ⬛ |
| Nextcloud integration | ⬛ | ⬛ | ⬛ |

\* Advanced questions are questions that require searching on the internet

## Deployment

Currently it is meant to be deployed on a desktop or laptop computer. In theory you can deploy it on a small computer like a raspberry pi and replace a smart speaker.

### Requirements

\* Optional

\** Optional but recommended

\*** Optional but highly recommended

- Ollama
- Vosk model
- Internet connection
- [IP to airport server](https://github.com/sidgames5/ip-to-airport)
- Fast graphics card***

### Instructions

\* Optional

\** Advanced users only

1. Install Ollama
2. Download a [Vosk model](https://alphacephei.com/vosk/models)
3. Put the location of the Vosk model in the `vosk_model_path` in `main.py`
4. Set a custom wake word by changing `wake_word` in `main.py`*
5. Set a custom LLM model by changing `ai_model` in `main.py`**
6. Run `ollama serve` in a terminal window
7. Run the IP to airport server in a terminal window
8. Connect a microphone and speaker to your computer (you can use a built-in one)
9. Install the required python dependencies listed in the top of `main.py`
10. Follow the instructions in `personalization TEMPLATE.txt`
11. Enter the required API keys in `api_keys TEMPLATE.py` then rename it to `api_keys.py`
12. Run `python main.py` in a new terminal window
13. Give microphone access to the program if necessary
