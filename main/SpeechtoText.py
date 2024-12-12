import speech_recognition as sr

def speech_to_text(topic:str) -> str:
    while True:
        recognizer = sr.Recognizer()
        print(f"We asked 100 people: {topic}")
        with sr.Microphone(sample_rate=48000, chunk_size=2048) as source:
                print("Speak something...")
                audio_data = recognizer.listen(source, phrase_time_limit=5)
        try:
            text = recognizer.recognize_google(audio_data).lower()
            print("You said:", text)
            return text
        except sr.UnknownValueError:
            print("Sorry, could not understand audio. Please speak clearer")
            continue
        except sr.RequestError as e:
            print("Error: Could not request results from Google Speech Recognition service")
            continue