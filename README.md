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
The Web Service Needs a secret key for Django and an [Infura](https://infura.io/) ETH API Key to handle login with Web3.

You can get a free Infura ETH API key from [here](https://infura.io/product/ethereum).

Create a `.env` file in the project root and add your keys like shown below:

```
SECRET_KEY = 'XXXXXX'
WEB3_KEY = 'YYYYYY'
```

Run The Dev Server

```bash
python manage.py runserver
```
