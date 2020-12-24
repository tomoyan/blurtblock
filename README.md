# blurtblock  
https://blurtblock.herokuapp.com/  

Clone command (https) to local directory  
git clone https://github.com/tomoyan/blurtblock.git  

## Python  
1. Create virtual environment:  
python3 -m venv venv  

2. ACTIVATE venv (Ubuntu command):  
source venv/bin/activate  

3. Install all pakcages from requirements file:  
pip install -r requirements.txt  

DEACTIVATE venv (Ubuntu command):  
deactivate  

Create/Update requirements file:  
pip freeze > requirements.txt  

## UPDATE config.py  
Blurt Username and Posting Key:  
UPVOTE_ACCOUNT = os.environ.get('UPVOTE_ACCOUNT') or 'YOUR_USERNAME'  
UPVOTE_KEY = os.environ.get('UPVOTE_KEY') or 'YOUR_PRIVATE_POSTING_KEY'  

Firebase(realtime database) API key (firebase.google.com):  
FB_APIKEY = os.environ.get('FB_APIKEY') or 'YOUR_FB_APIKEY'  
https://github.com/nhorvath/Pyrebase4  

## FLASK APP  
Add flask environment variablea in .flaskenv file:  
touch .flaskenv  

FLASK_APP=app.py  
FLASK_ENV=development  
SECRET_KEY=YOUR_SECRET_KEY  

Run flask app:  
flask run  
