# Quizly Backend

Quizly turns a YouTube video into a quiz. The backend downloads the audio of
the video, transcribes it with Whisper and lets Gemini Flash create a quiz
with 10 questions and 4 answer options each.

This repository contains the REST API built with Django and Django REST
Framework. The matching frontend is available here:
https://github.com/Developer-Akademie-Backendkurs/project.Quizly

## Table of contents

- [Features](#features)
- [Requirements](#requirements)
- [Install FFmpeg](#install-ffmpeg)
- [Installation](#installation)
- [Using the frontend](#using-the-frontend)
- [API endpoints](#api-endpoints)
- [Notes on quiz generation](#notes-on-quiz-generation)
- [Project structure](#project-structure)

## Features

- Registration, login, logout and token refresh
- JWT authentication with HTTP-only cookies and a token blacklist on logout
- Quiz generation from a YouTube URL (yt-dlp, Whisper, Gemini Flash)
- List, view, edit and delete your own quizzes
- Admin panel to edit quizzes and single questions

## Requirements

- Python 3.10 or newer (developed with Python 3.12)
- **FFmpeg must be installed globally.** Whisper needs it to read audio files.
- A free Gemini API key from https://ai.google.dev/

## Install FFmpeg

macOS:

```bash
brew install ffmpeg
```

Windows:

```bash
winget install --id Gyan.FFmpeg -e --source winget
```

Linux (Debian/Ubuntu):

```bash
sudo apt install ffmpeg
```

Check the installation on any system:

```bash
ffmpeg -version
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/shajib07/quizly-backend.git
```

Open the project folder:

```bash
cd quizly-backend
```

### 2. Create a virtual environment

macOS / Linux:

```bash
python3 -m venv env
```

Windows:

```bash
python -m venv env
```

### 3. Activate the virtual environment

macOS / Linux:

```bash
source env/bin/activate
```

Windows:

```bash
env\Scripts\activate
```

### 4. Install the dependencies

Whisper installs PyTorch, so this takes a while.

```bash
pip install -r requirements.txt
```

### 5. Create your `.env` file

macOS / Linux:

```bash
cp .env.template .env
```

Windows:

```bash
copy .env.template .env
```

### 6. Fill in the values in `.env`

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` for local development |
| `ALLOWED_HOSTS` | Comma-separated hosts of the backend |
| `CORS_ALLOWED_ORIGINS` | Comma-separated URLs of the frontend |
| `GEMINI_API_KEY` | Your Gemini API key |
| `GEMINI_MODELS` | Gemini models to try, in this order |
| `WHISPER_MODEL` | Whisper model size, for example `tiny`, `base` or `small` |

You can create a secret key with this command:

```bash
python -c "from django.core.management.utils import get_random_secret_key as key; print(key())"
```

### 7. Create the database

```bash
python manage.py migrate
```

### 8. Create an admin user

```bash
python manage.py createsuperuser
```

### 9. Start the server

```bash
python manage.py runserver
```

The API runs at http://127.0.0.1:8000/api/ and the admin panel at
http://127.0.0.1:8000/admin/.

## Using the frontend

1. Clone the frontend repository.
2. Open it with a local web server, for example Live Server in VS Code.
3. Open it at `http://127.0.0.1:5500`. Do not use `localhost:5500`, because
   the browser would then not send the login cookies to the backend.

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/register/` | Create a new user |
| POST | `/api/login/` | Log in and set the auth cookies |
| POST | `/api/logout/` | Log out and blacklist the refresh token |
| POST | `/api/token/refresh/` | Set a new access token cookie |
| POST | `/api/quizzes/` | Create a quiz from a YouTube URL |
| GET | `/api/quizzes/` | List your quizzes |
| GET | `/api/quizzes/{id}/` | Get one quiz |
| PATCH | `/api/quizzes/{id}/` | Change the title or description |
| DELETE | `/api/quizzes/{id}/` | Delete a quiz and its questions |

All quiz endpoints require a logged-in user. Users can only access their own
quizzes.

## Notes on quiz generation

- The first quiz takes longer, because Whisper downloads its model once.
- The request waits until the quiz is ready. Depending on the video length
  and the load on the Gemini API this takes from a few seconds to a few
  minutes.
- If the first Gemini model is unavailable, the next one from
  `GEMINI_MODELS` is used.
- yt-dlp recommends a JavaScript runtime for YouTube downloads. If downloads
  fail, install Deno and update yt-dlp.

Install Deno on macOS:

```bash
brew install deno
```

Install Deno on Windows:

```bash
winget install --id DenoLand.Deno
```

Update yt-dlp:

```bash
pip install -U yt-dlp
```

## Project structure

```
quizly-backend/
├── core/        # Project settings and root URLs
├── auth_app/    # Registration, login, logout, token refresh
│   ├── api/     # Serializers, views and URLs
│   ├── authentication.py
│   └── utils.py
├── quiz_app/    # Quiz models, admin and quiz generation
│   ├── api/     # Serializers, views, URLs and permissions
│   ├── exceptions.py
│   ├── models.py
│   └── utils.py
├── manage.py
└── requirements.txt
```
