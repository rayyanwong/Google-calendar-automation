import datetime as dt
import os.path
import customtkinter as ctk

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar']
        
def getEvents(creds):
    try: 
        service = build("calendar","v3",credentials=creds)
        now = dt.datetime.now().isoformat() + "Z"
        event_result = service.events().list(calendarId="primary", timeMin= now, maxResults = 20, singleEvents = True, orderBy="startTime").execute()
        events = event_result.get("items",[])

        if not events:
            print("No upcoming events found!")
            return
        
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])
    except HttpError as error:
        print("Error occured: ",error)

def addEvent(creds,startTime,endTime,eventName,eventLocation):
    start_formatted = startTime.isoformat() + 'Z'
    end_formatted = endTime.isoformat() + 'Z'

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

# def setLocationBoxVar(choice):
#     locationBoxVar.set(choice)
    

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
        addEvent(creds,dt.datetime.utcnow(),dt.datetime.utcnow()+dt.timedelta(hours=1),nameEntryVar.get(),locationBoxVar.get())
        print("Success")

    ctk.set_appearance_mode('dark')
    ctk.set_default_color_theme('dark-blue')
    
    root = ctk.CTk()
    root.geometry("1080x600")

    frame = ctk.CTkFrame(master=root)
    frame.pack(pady=20,padx=60,fill="both",expand=True)

    label = ctk.CTkLabel(master=frame, text="Automated Calender system",font=("Roboto",30))
    label.pack(pady=12,padx=10)

    nameEntryVar = ctk.StringVar(value="")
    nameEntry = ctk.CTkEntry(master=frame, placeholder_text="Name of event",textvariable=nameEntryVar,width=200)
    nameEntry.pack(pady=12,padx=10)

    locationBoxVar = ctk.StringVar(value="BN Mess")
    locationChoice = ctk.CTkComboBox(master=frame,values=["BN Mess","Conference Room"],variable=locationBoxVar,width=200)
    # locationBoxVar.set("BN Mess")
    locationChoice.pack(pady=12,padx=10)

    submitBtn = ctk.CTkButton(master=frame,text="Add to calender",command=executeAdd)
    submitBtn.pack(pady=12,padx=10)

    root.mainloop()

if __name__ == "__main__":
    main()