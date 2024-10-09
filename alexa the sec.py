import os
from unittest import expectedFailure

import speech_recognition as sr
import pyttsx3
import webbrowser
import datetime
import whisper
import pyaudio
import numpy as np
import tempfile
import wave
import time
import wikipedia
import pyjokes
import requests
import json
import datetime as dt
import meteomatics.api as api


os.environ["WHISPER_FFMPEG"] = "C:/ffmpeg/bin/ffmpeg.exe"

# recognizer = sr.recognizers

engine = pyttsx3.init()

# Load the Whisper model
model = whisper.load_model("small")

def speak(text):
    engine.say(text)
    engine.runAndWait()


def play_music():
    # Step 1: Wait for user to say they want to play music
    speak("Do you want to play some music?")
    confirmation = listen()  # listens for user response (Yes/No)

    if "yes" in confirmation.lower():
        # Step 2: Ask the user what song they want to hear
        speak("What song would you like to hear?")
        song_name = listen()  # listens for the song name

        # Step 3: If song name is provided, search and play the song
        if song_name:
            search_url = f"https://www.youtube.com/results?search_query={song_name.replace(' ', '+')}"
            webbrowser.open(search_url)
            speak(f"Playing {song_name} on YouTube.")
        else:
            speak("I didn't catch the song name. Please try again.")
    else:
        speak("Okay, let me know when you're ready to play music.")

def listen():
    # Create a recognizer object
    recognizer = sr.Recognizer()

    # Use the microphone as the audio source
    with sr.Microphone() as source:
        print("listening...")
        recognizer.adjust_for_ambient_noise(source)

        # Capture the audio from the microphone
        audio_data = recognizer.listen(source)

        audio_file = "temp.wav"

        # Save the audio to a file
        with open(audio_file, "wb") as f:
            f.write(audio_data.get_wav_data())
            time.sleep(1)

    try:
        # Load the audio file with Whisper
          # Create an audio object from bytes
        result = model.transcribe(audio_file)

        text = result['text']
        print("You said: " + text)
        return text
    except Exception as e:
        print(f"Sorry, there was an error with the transcription: {e}")
        return None

def tell_time():
    now = datetime.datetime.now()

    current_time = now.strftime("%H:%M")

    speak(f"current time is {current_time}")

def main():
    speak(f"how can i help you today?")

    while True:
        command = listen()
        command = command.lower()
        if 'play music' in command:

            song_name = command.replace(' ', '+').strip()
            play_music()
        elif 'time' in command:
            tell_time()

        elif ('weather' in command) or ('Whether' in command):
            check_weather(command)

        elif 'search' in command:
            search_information(command)
        elif ('joke' in command) or ('tell me some jokes' in command):
            tell_dad_jokes(command)

        elif 'exit' in command:
            speak("goodbye")
            break

def search_information(query):
    if 'search' in query:
        search_terms = query.replace('search', '').strip()
        if search_terms:
            try:
                summary = wikipedia.summary(search_terms, sentences=2)
                speak(summary)
            except wikipedia.exceptions.DisambiguationError as e:
                speak(f"Ambiguous search, please be more specific. Options include: {', '.join(e.options[:5])}")
            except wikipedia.exceptions.PageError:
                 speak("Sorry, I couldn't find any information on that topic.")

        else:
            speak("Please provide a search term for Wikipedia.")

    elif 'google' in query:

        search_term = query.replace('google', '').strip()
        if search_term:
            search_url = f"https://www.google.com/search?q={search_term.replace(' ', '+')}"
            webbrowser.open(search_url)
            speak(f"Searching Google for {search_term}.")
        else:
            speak("Please provide a search term for Google.")

    elif 'youtube' in query:

        search_term = query.replace('youtube', '').strip()
        if search_term:
            search_url = f"https://www.youtube.com/results?search_query={search_term.replace(' ', '+')}"
            webbrowser.open(search_url)
            speak(f"Searching YouTube for {search_term}.")
        else:
            speak("Please provide a search term for YouTube.")

    else:
        speak("Sorry, I didn't understand where to search. Please specify Wikipedia, Google, or YouTube.")


def tell_dad_jokes(command):
    # Step 1: Listen for the initial joke request

    if command and ("joke" in command or "tell me some jokes" in command):
        # Assistant confirms
        speak("Do you want to hear some dad jokes?")

        # Step 2: Listen for confirmation
        confirmation = listen()

        if confirmation and "yes" or "sure" in confirmation.lower():
            # Tell a random dad joke using pyjokes
            joke = pyjokes.get_joke(category='neutral')  # You can also use 'chuck' or 'all'
            speak(joke)
        else:
            speak("Alright, maybe later!")

def get_weather(city_coordinates):
    parameters = ['t_2m:C', 'precip_1h:mm', 'wind_speed_10m:ms']
    startdate = dt.datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    enddate = startdate + dt.timedelta(days=1)
    interval = dt.timedelta(hours=1)

    username = 'personalproject_erfani_ali'  # Replace with your Meteomatics username
    password = 'gQ7H0drZk1'  # Replace with your Meteomatics password

    try:
        df = api.query_time_series([city_coordinates], startdate, enddate, interval, parameters, username, password)
        temperature = df.iloc[0]['t_2m:C']
        precipitation = df.iloc[0]['precip_1h:mm']
        wind_speed = df.iloc[0]['wind_speed_10m:ms']
        return f"The temperature is {temperature}°C, with {precipitation} mm of precipitation, and wind speed of {wind_speed} m/s."
    except Exception as e:
        return f"An error occurred while fetching the weather: {e}"

def check_weather(command):
    if 'weather in' in command:
        city = command.split("in")[-1].strip()

        # Get city coordinates via an API (like geocoding API)
        geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}"
        try:
            response = requests.get(geocoding_url)
            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    city_coordinates = (data['results'][0]['latitude'], data['results'][0]['longitude'])
                    weather_info = get_weather(city_coordinates)
                    speak(weather_info)
                else:
                    speak(f"Sorry, I couldn't find the coordinates for {city}.")
            else:
                speak(f"Error: Unable to fetch coordinates for {city}.")
        except Exception as e:
            speak(f"An error occurred while fetching the coordinates: {e}")
    else:
        speak("Please specify the city by saying 'weather in [city]'.")


if __name__ == "__main__":
    main()