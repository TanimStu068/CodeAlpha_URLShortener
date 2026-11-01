A simple URL shortener built with **Flask** and **SQLite** for the CodeAlpha
Backend Development Internship (Task 1).

## Features
- `POST /api/shorten` creates a unique 6-character short code for a long URL
- Mapping of short code to original URL stored in SQLite
- `GET /<code>` redirects to the original URL (and counts the click)
- Input validation (only absolute http/https URLs); duplicate URLs reuse their code
- Optional frontend to shorten links, copy them, and see recent links
- Automated tests with pytest

## Project structure
```
URLShortener/
├── app.py            # Flask app: routes + API
├── config.py         # Settings
├── database.py       # SQLite connection + schema
├── utils.py          # Code generation + URL validation
├── requirements.txt
├── templates/        # index.html, 404.html
├── static/           # style.css, app.js
└── tests/test_app.py
```

## Run locally
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## API

### Shorten a URL
```bash
curl -X POST http://127.0.0.1:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/some/very/long/path"}'
```
Response (`201`):
```json
{
  "short_code": "aZ3k9Q",
  "short_url": "http://127.0.0.1:5000/aZ3k9Q",
  "original_url": "https://example.com/some/very/long/path"
}
```
Errors return `400` with `{"error": "..."}`.

### Redirect
`GET /aZ3k9Q` responds with `302` to the original URL. Unknown codes return `404`.

### Stats
`GET /api/stats/<code>` returns the original URL, click count and creation time.

### Recent links
`GET /api/urls` returns the 20 most recent links.

## Tests
```bash
pytest
```

## Database schema
| column | type | notes |
|---|---|---|
| id | INTEGER | primary key |
| short_code | TEXT | unique |
| original_url | TEXT | |
| clicks | INTEGER | default 0 |
| created_at | TEXT | default current timestamp |
