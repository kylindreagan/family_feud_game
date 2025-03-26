import speech_recognition as sr
from PyQt5.QtWidgets import QLabel, QApplication
from time import sleep

def speech_to_text(topic:str, topic_label=None, info_label=None) -> str:
    while True:
        recognizer = sr.Recognizer()
        if topic_label == None:
            print(f"We asked 100 people: {topic}")
        else:
            topic_label.setText(f"We asked 100 people: {topic}")
            QApplication.processEvents()
        with sr.Microphone(sample_rate=48000, chunk_size=2048) as source:
                if info_label == None:
                    print("Speak something...")
                else:
                    info_label.setText("Speak something...")
                    QApplication.processEvents()
                audio_data = recognizer.listen(source, phrase_time_limit=5)
        try:
            #Google's Speech Recognition for regular recognition
            text = recognizer.recognize_google(audio_data).lower()
            return text
        except sr.UnknownValueError:
            if info_label == None:
                print("Sorry, could not understand audio. Please speak clearer")
                continue
            else:
                info_label.setText("Sorry, could not understand audio. Please speak clearer")
                QApplication.processEvents()
                sleep(.5)
                continue


        except sr.RequestError as e:
            print("Error: Could not request results from Google Speech Recognition service")
            continue
    
def speech_to_text_offline(topic: str) -> str:
    recognizer = sr.Recognizer()
    print(f"We asked 100 people: {topic}")
    while True:
        try:
            with sr.Microphone(sample_rate=48000, chunk_size=2048) as source:
                print("Speak something...")
                recognizer.adjust_for_ambient_noise(source, duration=1)  # Adjust to noise level
                audio_data = recognizer.listen(source, phrase_time_limit=5)
            
            #PocketSphinx for offline recognition
            text = recognizer.recognize_sphinx(audio_data).lower()
            return text
        except sr.UnknownValueError:
            print("Sorry, could not understand audio. Please speak clearer.")
        except sr.RequestError as e:
            print("Error: Could not process audio input. Make sure offline support is available.")

def speech_to_text_vosk(topic:str) -> str:
    #TO BE SET UP
    return ""