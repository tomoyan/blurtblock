# blurtblock  
https://blurtblock.herokuapp.com/  

Clone command (https) to local directory  
git clone https://github.com/tomoyan/blurtblock.git  

## Python  
Create virtual environment:  
python3 -m venv venv  

ACTIVATE venv (Ubuntu command):  
source venv/bin/activate  

DEACTIVATE venv (Ubuntu command):  
deactivate  

Install all pakcages from requirements file:  
pip install -r requirements.txt  

Create/Update requirements file:  
pip freeze > requirements.txt  

## UPDATE config.py  
Blurt Username and Posting Key:  
UPVOTE_ACCOUNT = os.environ.get('UPVOTE_ACCOUNT') or 'YOUR_USERNAME'  
UPVOTE_KEY = os.environ.get('UPVOTE_KEY') or 'YOUR_PRIVATE_POSTING_KEY'  

Firebase(realtime database) API key (firebase.google.com):  
FB_APIKEY = os.environ.get('FB_APIKEY') or 'YOUR_FB_APIKEY'  

## FLASK APP  
Run flask app on development  
export FLASK_APP=app.py  
export FLASK_ENV=development  
flask run  
