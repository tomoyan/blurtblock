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

Install beem with pip:  
pip install -U beem  

Install pakcages:  
pip install -r requirements.txt  

Create/Update requirements file:  
pip freeze > requirements.txt  

## FLASK APP  
Run flask app on development  
export FLASK_APP=app.py  
export FLASK_ENV=development  
flask run  
