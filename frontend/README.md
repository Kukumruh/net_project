# SUSU HelpDesk — React frontend

React + TypeScript + Vite client for the existing FastAPI API.

## Run locally

1. Start the backend and PostgreSQL as described in `docs/API.md`.
2. Copy `.env.example` to `.env` and set `VITE_API_URL` if the API is not at `http://localhost:8000/api/v1`.
3. From this directory run:

```bash
npm install
npm run dev
```

Open http://localhost:5173.

## Implemented API operations

- `POST /auth/login` — JSON email/password, JWT Bearer.
- `GET /categories` — category selector.
- `GET /requests?limit=&offset=` — current user's requests.
- `GET /requests/{id}` — request details.
- `POST /requests` — create request.
- `PATCH /requests/{id}` — edit title/description while the request is new.

The API only exposes a user's own requests. Editing is limited by the backend to requests in the "Новая" state. Operator tools, comments, attachments and knowledge base are not part of the current API and are not simulated.

The token is held in sessionStorage so closing the browser tab/session clears it. Configure backend CORS to allow `http://localhost:5173` for local development.
