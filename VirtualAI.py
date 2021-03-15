from __future__ import print_function
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime
import pickle
import os.path
import os
import time
import playsound
import speech_recognition as sr
from gtts import gTTS
import pytz
import subprocess
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
DAYS = ["monday", "tuesday", "wednesday","thursday", "friday", "saturday", "sunday"]
MONTHS = ["january", "february", "march", "april", "may","june", "july", "august", "september", "october", "november", "december"]
DAY_EXTENSIONS = ["rd", "th", "st"]


def speak(text):
    tts = gTTS(text=text)
    filename = "voice.mp3"
    tts.save(filename)
    playsound.playsound(filename)
    os.remove(filename)
def audio():
    recon = sr.Recognizer()
    with sr.Microphone() as source:
        audio =recon.listen(source)
        said = ""
        try:
            said =  recon.recognize_google(audio)
            print(said)
        except Exception as e:
            print("Exception" + str(e))
    return said.lower()
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
def calendar():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('calendar', 'v3', credentials=creds)
    return service
def get_events(day, service):
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.UTC
    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)
    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(),timeMax=end_date.isoformat(),
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    if not events:
        print('No upcoming events found.')
    else:
        speak(f"You have {len(events)} events on this day.")
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start,event['summary'])
        start_time = str(start.split("T")[1].split("-")[0])
        if int(start_time.split(":")[0]) < 12:
            start_time = start_time + "am"
        else:
            start_time = str(int(start_time.split(":")[0])- 12) + start_time.split(":")[1]
            start_time = start_time + "pm"

        speak(event["summary"] + " at " + start_time)
def get_date(text):
    text = text.lower()
    today = datetime.date.today()
    if text.count("today") > 0:
        return today
    day = -1
    day_of_the_week = -1
    month = -1
    year = today.year

    for x in text.split():
        if x in MONTHS:
            month = MONTHS.index(x) + 1
        elif x in DAYS:
            day_of_the_week = DAYS.index(x)
        elif x.isdigit():
            day = int(x)
        else:
            for ext in DAY_EXTENSIONS:
                found = x.find(ext)
                if found > 0:
                    try:
                        day = int(x[:found])
                    except:
                        pass
    if month < today.month and month != -1:
         year = year + 1
    if day < today.day and month == -1 and day != -1:
        month = month + 1
    if month == -1 and day == -1 and day_of_the_week != -1:
        current_day_of_the_week = today.weekday()
        diff =  day_of_the_week - current_day_of_the_week
        if diff < 0:
            diff = diff + 7
            if text.count("next") >= 1:
                diff = diff + 7
        return today + datetime.timedelta(diff)
    if month == -1 or day == -1:
        return None
    return datetime.date(month=month, day=day, year=year)
def note(text):
    date = datetime.datetime.now()
    fn = str(date).replace(":","-") + "-note.txt"
    with open(fn, "w") as f:
        f.write(text)
    cpp = "C:\Program Files (x86)\Dev-Cpp\devcpp.exe"
    subprocess.Popen([cpp, fn])
def google(text):
    date = datetime.datetime.now()
    fn = str(date).replace(":","-") + "-note.txt"
    with open(fn, "w") as f:
        f.write(text)
    gog = "C:\Program Files\Google\Chrome\Application\chrome.exe"
    subprocess.Popen([gog])
def steam(text):
    date = datetime.datetime.now()
    fn = str(date).replace(":","-") + "-note.txt"
    with open(fn, "w") as f:
        f.write(text)
    stm = "D:\Cosas\steam.exe"
    subprocess.Popen([stm])

wakeup = "Hello Cortina"
service = calendar()
print("Listening..")
text = audio()

text = audio()
if text.count(wakeup) > 0:
    speak("Hello Master! I'm ready.")
    text = audio()
    CALENDAR = [ "what i have ", "do i have something", "i have plans", "i am busy", "i am free", "i have something"]
    for x in CALENDAR:
        if x in text.lower():
            date = get_date(text)
            if date:
                get_events(date, service)
            else:
                speak("Nothing found.")
    NOTE_STRS  = ["make a note", "write", "write this", "remember this", "take a note"]
    for x in NOTE_STRS:
        if x in text:
            speak("What would you like me to write?")
            note_pad = audio().lower()
            note(note_pad)
            speak("Written!")
    GOOGLE_STRS = ["open google", "go to google", "run google", "Google"]
    for x in GOOGLE_STRS:
        if x in text:
            speak("Openning Google...")
            google_open = audio().lower()
            google(google_open)
            speak("Google is Running")
    STEAM_STRS = ["open steam", "buy a game", "Steam", "open Steam"]
    for x in STEAM_STRS:
        if x in text:
            speak("Openning Steam...")
            steam_open = audio().lower()
            steam(steam_open)
            speak("Steam is Running")
