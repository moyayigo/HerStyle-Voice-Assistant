![show demo](gui.gif)
# HerStyle-Voice-Assistant
HerStyleVoiceAI is a Python-based voice assistant application that combines speech recognition (ASR), audio capture, and dialogue processing capabilities. It provides a graphical user interface that supports recording, speech recognition, and interaction with backend services.

## Run environment
   Windows11 with TTS

## Installation

1. Download and Install Ollama:
   [https://ollama.com/](https://ollama.com/)
   
2. Run a ollama model and modification recording_answer_thread.py module:
   ```bash
   generate_kwargs = {
      'model': 'your ollama moedl name',
      'prompt': clean_text,
      'stream': True
   }
   ```

2. Install dependencies：
   ```bash
   pip install pyaudio requests PyQt5
   ```

3. Download the project code and enter the project directory

4. Run the main program：
   ```bash
   python main.py
   ```
