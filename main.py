from datetime import datetime, timedelta, timezone
import os.path
import customtkinter as ctk
from tkcalendar import DateEntry,Calendar
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar']
        
def getEvents(creds):
    try: 
        service = build("calendar","v3",credentials=creds)
        now = datetime.now().isoformat() + "Z"
        event_result = service.events().list(calendarId="primary", timeMin= now, maxResults = 5, singleEvents = True, orderBy="startTime").execute()
        events = event_result.get("items",[])

        if not events:
            print("No upcoming events found!")
            return
        
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])
    except HttpError as error:
        print("Error occured: ",error)

def addEvent(creds,startTime: datetime ,endTime: datetime,eventName,eventLocation):
    local_tz = timezone(timedelta(seconds=-time.timezone))    
    start_formatted = (startTime - timedelta(seconds=-time.timezone)).isoformat() + 'Z'
    end_formatted = (endTime- timedelta(seconds=-time.timezone)).isoformat()  + 'Z'
    print(start_formatted)
    print(end_formatted)

    event = {
        'summary': eventName,
        'location': eventLocation,
        'start': {
            'dateTime': start_formatted,
            'timeZone': 'Singapore'
        },
        'end': {
            'dateTime': end_formatted,
            'timeZone': 'Singapore'
        },

    }

    service = build('calendar','v3',credentials=creds)
    event = service.events().insert(calendarId='primary',body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))
  

def main():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token: 
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json","w") as token:
            token.write(creds.to_json())
        
    def executeAdd():
        eventTitle = f'({unitEntry.get()}) {nameEntry.get()}'
        startTime = datetime(2023,8,23,20,30,00)
        endTime = datetime(2023,8,23,22,30,00)  
        addEvent(creds,startTime,endTime,eventTitle,locationBoxVar.get())
        print("Success")
        cal.set_date(datetime.today())
        nameEntry.delete(0,'end')
        unitEntry.delete(0,'end')
        locationBoxVar.set("BN Mess")

    def executeGet():
        getEvents(creds)


    ctk.set_appearance_mode('dark')
    ctk.set_default_color_theme('dark-blue')
    
    root = ctk.CTk()
    root.geometry("1080x600")

    frame = ctk.CTkFrame(master=root)
    frame.pack(pady=20,padx=60,fill="both",expand=True)

    label = ctk.CTkLabel(master=frame, text="Automated Calender system",font=("Roboto",30))
    label.pack(pady=12,padx=10)

    nameEntry = ctk.CTkEntry(master=frame, placeholder_text="Name of event",width=200)
    nameEntry.pack(pady=12,padx=10)

    unitEntry = ctk.CTkEntry(master=frame,placeholder_text="Unit hosting event",width=200)
    unitEntry.pack(pady=12,padx=10)

    locationBoxVar = ctk.StringVar(value="BN Mess")
    locationChoice = ctk.CTkComboBox(master=frame,values=["BN Mess","Conference Room"],variable=locationBoxVar,width=200)
    # locationBoxVar.set("BN Mess")
    locationChoice.pack(pady=12,padx=10)

    cal = DateEntry(master=frame, width=30, background='darkblue',
                    foreground='dark', borderwidth=2)
    cal.pack(padx=10, pady=12)

    submitBtn = ctk.CTkButton(master=frame,text="Add to calender",command=executeAdd)
    submitBtn.pack(pady=12,padx=10)

    getEventsBtn = ctk.CTkButton(master=frame,text="Get next 5 events",command=executeGet)
    getEventsBtn.pack(pady=12,padx=10)

    root.mainloop()

if __name__ == "__main__":
    main()