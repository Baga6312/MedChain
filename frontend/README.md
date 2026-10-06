# MedChain Frontend

React (Vite) UI for the MedChain healthcare API. Served by nginx; `/api/*` is proxied to the Django backend.

## Run

```bash
docker compose up -d --build     # from the repo root
```

Open `http://localhost` (gateway on port 80). `http://localhost:5173` serves the static build only, without `/api`.

Dev mode: `npm install && npm run dev` (needs a Vite proxy for `/api` -> `http://localhost:8000`).

## Structure

```
src/
├── main.jsx        entry point
├── App.jsx         shell: sidebar + toast
├── CrudPage.jsx    generic list / create / edit / delete page
├── resources.js    resource config: labels, form fields, foreign keys
├── api.js          fetch client for /api
├── styles.css      base styles
└── crud.css        form and table styles
```

To add a resource, add an entry to `resources.js`; no other file changes.

---

# API reference

Base URL: `/api`. All bodies are JSON.

| Resource | Path | Fields |
|---|---|---|
| Doctors | `/api/doctors/` | `id`*, `name`, `specialty` |
| Patients | `/api/patients/` | `id`*, `name`, `birth_date` (nullable), `phone` |
| Appointments | `/api/appointments/` | `id`*, `patient` (id), `doctor` (id), `date`, `notes`, `status` |
| Medical records | `/api/medical-records/` | `id`*, `patient` (id), `title`, `content`, `created_at`*, `updated_at`* |

\* read-only, assigned by the server. All other fields are required.

Detail routes: `/api/<resource>/<id>/`

## Endpoints

| Method | Path | Request | Success |
|---|---|---|---|
| GET | `/<resource>/` | no query params, no body | `200` array of objects |
| GET | `/<resource>/<id>/` | no query params, no body | `200` object |
| POST | `/<resource>/` | JSON body, no query params | `201` (see below) |
| PUT | `/<resource>/<id>/` | JSON body **including `id`**, all fields | `200` `{"detail": "... updated."}` |
| DELETE | `/<resource>/<id>/` | no query params, no body | `200` `{"detail": "... deleted"}` (appointments: `204`, empty) |

POST response by resource:

| Resource | Response |
|---|---|
| Doctors, Medical records | `201` the created object |
| Patients | `201` `{"detail": "Patient has been created successfully."}` |
| Appointments | `201` `{"detail": "Appointment created."}` |

Notes:
- PUT identifies the row by the `id` in the **body**, and requires the full object (no partial updates).
- PATCH routes exist but behave like PUT; appointments reject PATCH (`405`).
- `Content-Type: application/json` is mandatory on POST and PUT.

## Examples

```bash
# list
curl http://localhost/api/doctors/

# create
curl -X POST http://localhost/api/doctors/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Dr. Priya Patel", "specialty": "Cardiology"}'

# update (id in body)
curl -X PUT http://localhost/api/doctors/1/ \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "name": "Dr. Priya Patel", "specialty": "Neurology"}'

# delete
curl -X DELETE http://localhost/api/doctors/1/
```

## Validation rules

- **Doctors:** `name` must be unique.
- **Patients:** `name` and `phone` must each be unique.
- **Appointments:**
  1. A patient can only be assigned to one doctor (across all their appointments).
  2. A patient cannot have two active (pending or on-going) appointments with the same doctor.
- **Medical records:** `patient`, `title`, `content` required.

## Errors

| Status | Body | Cause |
|---|---|---|
| `400` | `{"detail": "Error while processing the request."}` | Query params or body on GET/DELETE; query params or non-JSON content type on POST/PUT |
| `400` | `{"detail": "'id' is required in the body."}` | PUT without `id` |
| `400` | `{"detail": "..."}` | Duplicate name/phone (doctors, patients) |
| `400` | `{"field": ["message"]}` | Field validation, including appointment rules (`doctor` key) |
| `404` | `{"detail": "<Resource> not found."}` | Unknown id on PUT or DELETE |

The UI surfaces these messages in the form modal (create/edit) or a toast (delete).