# MedChain

HealthChain is a secure healthcare platform designed to enable patients, doctors, and administrators to securely manage and share healthcare data while ensuring privacy, controlled access, and reliable service availability.

## Backend avec Docker

Depuis la racine du projet, démarrer PostgreSQL et l'API Django :

```powershell
docker compose up --build
```

Le service backend attend la disponibilité de PostgreSQL, applique les migrations et charge les utilisateurs de démonstration avant de lancer Gunicorn.

URLs utiles :

- API : http://localhost:8000/api/
- Documentation Swagger : http://localhost:8000/api/docs/
- Schéma OpenAPI : http://localhost:8000/api/schema/

Comptes de démonstration créés par `python manage.py seed` :

- `patient1` à `patient5`
- `doctor1` à `doctor3`
- `admin`
- Mot de passe : `DemoPass123!`

Arrêter les services :

```powershell
docker compose down
```


