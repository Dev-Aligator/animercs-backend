# Anime Recommendation Backend

This Repository is a REST API built with Django, aimed at providing anime recommendations based on user preferences. The API utilizes Django to manage user authentication, store anime data, and generate recommendations dynamically.

## API Endpoints

### Authentication:

- `POST /api/auth/register/`: Register a new user.
- `POST /api/auth/login/`: Login and obtain an authentication token.
- `POST /api/auth/logout/`: Logout and invalidate the authentication token.

### Anime Data:

- `GET /api/anime/`: List all anime entries.
- `POST /api/anime/`: Add a new anime entry.
- `GET /api/anime/<id>/`: Retrieve details of a specific anime.
- `PUT /api/anime/<id>/`: Update details of a specific anime.
- `DELETE /api/anime/<id>/`: Delete a specific anime entry.

### Recommendations:

- `GET /api/recommendations/`: Get personalized anime recommendations for the authenticated user.

## Setup

1. **Clone the repository:**

```bash
    git clone https://github.com/Dev-Aligator/animercs-backend.git 
```


<details>
<summary>
&nbsp;2.<strong> Create Virtual Environment:</strong>

</summary>

Creating Virtual Environment named `env`

```bash
    python -m venv env
```

To Activate `env` (on Linux bash/zsh), checkout the <a href="https://docs.python.org/3/library/venv.html#how-venvs-work" >venv docs</a> for other flatforms

```bash
    source env/bin/activate
```

To deactivate `env`

```bash
deactivate
```
</details>

---


3. **Install dependencies:**
```bash
    pip install -r requirements.txt
```

<details>
<summary>
&nbsp;4.<strong> Setup Database:</strong>

</summary>

Making database migrations

```bash
    python manage.py makemigrations
    python manage.py migrate
```

</details>

---
5. **Creating superuser to access Admin Panel:**
```bash
    python manage.py createsuperuser
```

6. **Run the Server:**
```bash
    python manage.py runserver
```

---



<p align="center">Dev-Aligator</p>
<p align="center">
<a href="https://github.com/Dev-Aligator/">
<img src="https://user-images.githubusercontent.com/58631762/120077716-60cded80-c0c9-11eb-983d-80dfa5862d8a.png" width="19">
</a>