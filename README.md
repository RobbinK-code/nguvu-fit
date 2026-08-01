# Nguvu Fit

A home-workout app: personalized weekly training plans, progress tracking,
daily motivation, subscriptions via M-Pesa, and an admin panel.

- **Backend**: Flask + SQLAlchemy + Marshmallow + Flask-JWT-Extended, deployed on Render with Postgres.
- **Frontend**: React (Vite), deployed on Vercel.
- **Payments**: M-Pesa Daraja API (STK Push).

## Project Structure

```
nguvu-fit/
├── backend/     Flask API
└── frontend/    React app
```

## How the recommendation engine works

`backend/recommend.py` is a rule-based scoring/selection algorithm, not a
call to an external AI model:

1. Computes BMI and, if a target weight/date are set, the weekly rate of
   change needed to hit it - flagging anything faster than ~1kg/week as an
   aggressive pace.
2. Picks a cardio/strength/mobility mix based on the user's goal.
3. Filters the exercise catalog down to what the user's equipment supports.
4. Prioritizes exercises in the user's chosen focus areas, and spreads
   picks across the week to avoid repeats.

It's deterministic per user per day (same plan if you refresh, new plan
tomorrow), free to run, and fully explainable - no external API key
required.

## Local Development

### Backend

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # fill in values, at minimum JWT_SECRET_KEY
export FLASK_APP=app.py
export $(cat .env | xargs)   # or use python-dotenv / your shell's env loading

flask db upgrade
python seed.py
flask run -p 5555
```

Run tests: `pytest` (from `backend/`).

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_URL=http://localhost:5555
npm run dev
```

## Deploying

### Backend → Render

1. Push this repo to GitHub.
2. In Render: **New → Blueprint**, point it at the repo. `backend/render.yaml`
   defines a web service plus a free Postgres database.
3. Render will prompt for the env vars marked `sync: false` in `render.yaml`
   (`FRONTEND_ORIGIN`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, and the `MPESA_*`
   vars). Set `FRONTEND_ORIGIN` once you know your Vercel URL, and leave the
   M-Pesa vars blank until you have Daraja credentials — the API will run
   fine without them; `/payments/subscribe` will just return a clear
   "not configured" error until they're set.
4. The build command runs migrations and seeds the catalog automatically.

### Frontend → Vercel

1. In Vercel: **New Project**, import the same repo, set the root directory
   to `frontend/`.
2. Set the environment variable `VITE_API_URL` to your Render backend URL
   (e.g. `https://nguvu-fit-api.onrender.com`).
3. Deploy. `frontend/vercel.json` handles the SPA rewrite so client-side
   routes work on refresh.
4. Back in Render, set `FRONTEND_ORIGIN` to your Vercel URL so CORS allows it.

### Enabling M-Pesa payments

1. Register at [developer.safaricom.co.ke](https://developer.safaricom.co.ke)
   and create an app to get a sandbox Consumer Key/Secret.
2. Sandbox testing uses Safaricom's shared shortcode `174379` and a shared
   passkey (both published on the Daraja docs/portal).
3. Set `MPESA_CALLBACK_URL` to `https://<your-render-url>/payments/callback`
   — this must be a publicly reachable HTTPS URL, so it only works once
   deployed, not on localhost.
4. Add all `MPESA_*` values in Render's environment settings and redeploy.
5. Move to production credentials (real shortcode/passkey, `MPESA_ENV=production`)
   once you've applied for and been approved for a paybill/till number.

## Admin Access

The seed script creates an admin account from `ADMIN_EMAIL` /
`ADMIN_PASSWORD` (defaults: `admin@nguvufit.com` / `changeme123` — **change
these** before deploying). Admins can view platform stats, promote/demote
other admins, and remove accounts at `/admin`.

## API Overview

| Area | Endpoints |
|---|---|
| Auth | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| Profile | `GET /profile`, `PATCH /profile` |
| Plan | `GET /plan?days=3` |
| Exercises | `GET /exercises`, `POST /exercises` (admin), `DELETE /exercises/<id>` (admin) |
| Logs | `GET /logs`, `POST /logs`, `GET /logs/stats` |
| Quotes | `GET /quotes/today` |
| Payments | `POST /payments/subscribe`, `POST /payments/callback`, `GET /payments/status/<id>` |
| Admin | `GET /admin/users`, `PATCH /admin/users/<id>/toggle-admin`, `DELETE /admin/users/<id>`, `GET /admin/stats` |

## Notes on Scope

- Subscription gating is enforced by `subscription_required` in
  `backend/decorators.py`, currently unused by any route out of the box —
  wire it onto whichever endpoints you want to reserve for paying users
  (e.g. a richer plan, longer history, etc).
- The recommendation engine and quotes are intentionally rule-based rather
  than calling an external LLM, so the app has no ongoing AI API costs and
  no dependency on a third-party key. If you'd rather have real AI-written
  quotes, that's a small addition to `routes/quotes.py` using your own
  Anthropic or OpenAI API key server-side.
