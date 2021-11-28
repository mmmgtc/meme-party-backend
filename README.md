# meme-party-backend
Backend Service for hosting the party

## Setup the Dev Server

First get the repo:

```bash
git clone https://github.com/mmmgtc/meme-party-backend/
cd meme-party-backend
```

Setup the Dependencies (We suggest using a seperate virtualenv)

```bash
pip install -r requirments.txt
```

Prepare the Database

```bash
python manage.py migrate
```

Run The Dev Server

```bash
python manage.py runserver
```
