# Voice Assistant

A simple voice assistant that respects your privacy.

## Features

🟥 Confirmed not working yet

🟨 Partially working/in development

🟩 Fully working

⬛ Not tested yet/not implemented

| Feature | Windows | MacOS | Linux |
|-|-|-|-|
| Basic questions | ⬛ | ⬛ | 🟩 |
| Advanced questions* | ⬛ | ⬛ | ⬛ |
| Time | ⬛ | ⬛ | 🟩 |
| Weather | ⬛ | ⬛ | 🟨 |
| Smart device control | ⬛ | ⬛ | ⬛ |

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
7. Connect a microphone and speaker to your computer (you can use a built-in one)
8. Install the required python dependencies listed in the top of `main.py`
9. Run `python main.py` in a new terminal window
10. Give microphone access to the program if necessary