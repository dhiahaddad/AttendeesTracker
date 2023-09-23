# AttendeesTracker

## Features:
- Days and Sessions are updated in the Sessions.xlsx (It's the input file).
- Scanned QR codes are stored in the Main file.xlsx (It's the output file).
- In this version, only TUC cloud is supported. Google forms will be supported in the next version.
- The app stores the name of the last scanned badge to avoid storing it again if the attendee do not take back his badge in time.
- The current session can be automatically identified based on its start time and the start time of the following session. You can update the current session by updating the start time in the Sessions.xlsx. When you update Sessions.xlsx, you should refresh the page to let the software get the updated data.

## To install:
```
git clone https://github.com/dhiahaddad/AttendeesTracker.git
cd AttendeesTracker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
