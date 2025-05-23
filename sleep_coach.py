import os
import json
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import speech_recognition as sr
import pyttsx3
import time
from datetime import datetime
import wave

class SleepCoach:
    def __init__(self):
        self.sleep_knowledge = self._load_sleep_knowledge()
        self.conversation_history = []
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        # Set properties for the voice
        self.engine.setProperty('rate', 150)    # Speed of speech
        self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
        self.state = {
            "topic": None,        # e.g., "insomnia", "sleep hygiene"
            "subtopic": None,     # e.g., "falling asleep", "staying asleep"
            "last_advice": None  # e.g., "basic", "detailed"
        }
        
    def _load_sleep_knowledge(self):
        """Load sleep-specific knowledge base"""
        return {
            "sleep_stages": {
                "N1": "Light sleep, transition between wakefulness and sleep",
                "N2": "Deeper sleep, body temperature drops, heart rate slows",
                "N3": "Deep sleep, important for physical recovery",
                "REM": "Rapid Eye Movement sleep, important for memory and learning"
            },
            "sleep_hygiene": [
                "Maintain consistent sleep schedule",
                "Create a dark, quiet, and cool sleep environment",
                "Limit exposure to blue light before bed",
                "Avoid caffeine and alcohol close to bedtime",
                "Exercise regularly but not close to bedtime"
            ],
            "common_issues": {
                "insomnia": "Difficulty falling or staying asleep",
                "sleep_apnea": "Breathing interruptions during sleep",
                "restless_legs": "Uncomfortable sensations in legs at night",
                "circadian_rhythm_disorder": "Misalignment of sleep-wake cycle"
            }
        }

    def record_audio(self, duration=5, sample_rate=16000):
        """Record audio from microphone"""
        print("Recording...")
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()
        print("Recording finished")
        
        # Save the recording in the correct format
        filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 2 bytes for int16
            wf.setframerate(sample_rate)
            wf.writeframes(recording.tobytes())
        return filename

    def transcribe_audio(self, audio_file):
        """Convert audio to text using speech_recognition"""
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio)
                return text
            except sr.UnknownValueError:
                return "Sorry, I couldn't understand that."
            except sr.RequestError:
                return "Sorry, there was an error with the speech recognition service."

    def generate_response(self, user_input):
        user_input = user_input.lower()
        # Multi-turn: handle yes/no and follow-ups
        if user_input in ['yes', 'yeah', 'sure', 'okay', 'ok']:
            if self.state["topic"] == "insomnia" and self.state["last_advice"] == "basic":
                self.state["last_advice"] = "detailed"
                return ("Here are some advanced tips for managing insomnia:\n"
                        "- Try cognitive behavioral therapy for insomnia (CBT-I)\n"
                        "- Avoid clock-watching at night\n"
                        "- Get out of bed if you can't sleep after 20 minutes\n"
                        "- Reserve your bed for sleep only\n"
                        "Would you like tips for falling asleep or staying asleep?")
            elif self.state["topic"] == "insomnia" and self.state["last_advice"] == "detailed":
                return ("For falling asleep: Try progressive muscle relaxation, deep breathing, or mindfulness meditation.\n"
                        "For staying asleep: Keep your bedroom cool, avoid large meals before bed, and manage stress.\n"
                        "Would you like to discuss another sleep issue?")
            elif self.state["topic"] == "sleep hygiene":
                return ("Would you like personalized sleep hygiene tips based on your routine? If so, tell me about your bedtime habits.")
            elif self.state["topic"] == "sleep apnea":
                return ("If you suspect sleep apnea, it's important to consult a healthcare provider. Would you like to know about lifestyle changes or medical treatments?")
            elif self.state["topic"] == "restless legs":
                return ("For restless legs, regular exercise and good sleep hygiene can help. Would you like more tips or information about medications?")
            elif self.state["topic"] == "circadian rhythm disorder":
                return ("Would you like advice on adjusting your sleep schedule or using light therapy?")
            else:
                return ("What specific aspect would you like to know more about? You can ask about sleep stages, sleep hygiene, or common sleep issues.")
        if user_input in ['no', 'nope', 'not now']:
            self.state = {"topic": None, "subtopic": None, "last_advice": None}
            return "Okay! Let me know if you have any other sleep questions."
        # Topic detection
        if any(issue in user_input for issue in ['insomnia']):
            self.state["topic"] = "insomnia"
            self.state["last_advice"] = "basic"
            return ("Insomnia is difficulty falling or staying asleep. Would you like some tips to manage insomnia?")
        if any(issue in user_input for issue in ['sleep apnea']):
            self.state["topic"] = "sleep apnea"
            self.state["last_advice"] = "basic"
            return ("Sleep apnea is breathing interruptions during sleep. Would you like advice on managing sleep apnea?")
        if any(issue in user_input for issue in ['restless legs']):
            self.state["topic"] = "restless legs"
            self.state["last_advice"] = "basic"
            return ("Restless legs syndrome causes uncomfortable sensations in your legs at night. Would you like tips to manage it?")
        if any(issue in user_input for issue in ['circadian rhythm']):
            self.state["topic"] = "circadian rhythm disorder"
            self.state["last_advice"] = "basic"
            return ("Circadian rhythm disorder is a misalignment of your sleep-wake cycle. Would you like advice on managing it?")
        if any(term in user_input for term in ['hygiene', 'routine', 'habit', 'schedule', 'improve', 'better']):
            self.state["topic"] = "sleep hygiene"
            self.state["last_advice"] = "basic"
            return self._get_sleep_hygiene_advice() + "\nWould you like more personalized tips?"
        if any(stage in user_input for stage in ['stage', 'n1', 'n2', 'n3', 'rem', 'rm']):
            self.state["topic"] = "sleep stages"
            self.state["last_advice"] = "basic"
            return self._get_sleep_stage_info(user_input)
        # Subtopic handling for insomnia
        if self.state["topic"] == "insomnia" and self.state["last_advice"] == "detailed":
            if "falling asleep" in user_input:
                return ("For falling asleep: Try progressive muscle relaxation, deep breathing, or mindfulness meditation.\n"
                        "Would you like more tips?")
            if "staying asleep" in user_input:
                return ("For staying asleep: Keep your bedroom cool, avoid large meals before bed, and manage stress.\n"
                        "Would you like more tips?")
        # Default response
        return ("I'm here to help with your sleep concerns. You can ask me about:\n- Sleep stages (N1, N2, N3, REM)\n- Sleep hygiene practices\n- Common sleep issues (insomnia, sleep apnea, etc.)")

    def _get_sleep_stage_info(self, query):
        """Get information about sleep stages"""
        stages = self.sleep_knowledge['sleep_stages']
        if 'n1' in query or 'stage 1' in query:
            return f"N1 sleep is {stages['N1']}"
        elif 'n2' in query or 'stage 2' in query:
            return f"N2 sleep is {stages['N2']}"
        elif 'n3' in query or 'stage 3' in query or 'deep' in query:
            return f"N3 sleep is {stages['N3']}"
        elif 'rem' in query or 'rm' in query or 'rapid' in query:
            return f"REM sleep is {stages['REM']}"
        else:
            return "There are four main stages of sleep:\n1. N1: Light sleep, transition between wakefulness and sleep\n2. N2: Deeper sleep, body temperature drops, heart rate slows\n3. N3: Deep sleep, important for physical recovery\n4. REM: Rapid Eye Movement sleep, important for memory and learning"

    def _get_sleep_hygiene_advice(self):
        """Get sleep hygiene advice"""
        advice = self.sleep_knowledge['sleep_hygiene']
        return "Here are some important sleep hygiene practices:\n" + "\n".join(f"- {item}" for item in advice)

    def text_to_speech(self, text):
        """Convert text to speech using pyttsx3"""
        self.engine.say(text)
        self.engine.runAndWait()

    def run_conversation(self):
        """Run a complete voice-to-voice conversation"""
        print("Sleep Coach: Hello! I'm your sleep coach. How can I help you today?")
        self.text_to_speech("Hello! I'm your sleep coach. How can I help you today?")
        
        while True:
            # Record user input
            audio_file = self.record_audio()
            
            # Transcribe user input
            user_input = self.transcribe_audio(audio_file)
            print(f"You: {user_input}")
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Sleep Coach: Goodbye! Sleep well!")
                self.text_to_speech("Goodbye! Sleep well!")
                break
            
            # Generate response
            response = self.generate_response(user_input)
            print(f"Sleep Coach: {response}")
            
            # Convert response to speech
            self.text_to_speech(response)
            
            # Clean up audio file
            os.remove(audio_file)

if __name__ == "__main__":
    coach = SleepCoach()
    coach.run_conversation() 