# YaTube social network 

Project supports authorization, personal feeds, comments and subscription to authors. \
It was written as a Python Django application using MVC and HTML templates using Twitter Bootstrap framework. Used SQLite db and covered with unittest.

### Run

Clone repo and create venv:

```
git clone git@github.com:sushidze/Yatube.git
cd Yatube

python -m venv env
. venv/bin/activate
```

Install requirements.txt:

```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Do Django migrations and run project:

```
python manage.py migrate

python manage.py runserver
```
