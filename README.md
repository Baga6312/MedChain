# MedChain / SecureHealthOps

MedChain est une plateforme expérimentale de gestion sécurisée de données médicales. Elle permet de présenter les parcours Patient, Médecin et Administrateur, le partage contrôlé de dossiers et la traçabilité des opérations sensibles.

## Ce qui a été ajouté

### Backend Django REST

- Authentification par token avec `POST /api/auth/login/`.
- Rôles `Patient`, `Médecin` et `Administrateur`.
- Modèles `MedicalRecord`, `AccessPermission`, `AuditLog` et `UserProfile`.
- Autorisation d'un médecin par le patient.
- Révocation d'une autorisation.
- Filtrage serveur des patients et dossiers accessibles.
- Réponse `403 Forbidden` lorsqu'un médecin tente un accès non autorisé.
- Journalisation des connexions, consultations, autorisations, révocations et refus.
- Documentation Swagger et schéma OpenAPI.
- Migration `healthcare.0002_security_models` et commande de seed de démonstration.

### Frontend React

Le projet React indépendant se trouve dans [frontend](frontend). Il contient :

- Page de connexion avec sélection du rôle.
- Dashboard Patient avec informations, rendez-vous et médecins autorisés.
- Actions d'autorisation et de révocation avec notifications.
- Dashboard Médecin avec liste des patients autorisés.
- Écran d'accès refusé `403`.
- Historique des accès avec utilisateur, action, date et résultat.
- Dashboard Administrateur avec indicateurs et événements de sécurité.
- Design responsive desktop/mobile inspiré du template Stitch.

Les écrans utilisent actuellement des données de démonstration. Le proxy Nginx `/api/` est déjà configuré pour le branchement avec l'API Django.

### Conteneurisation

- PostgreSQL 16 dans le service `db`.
- Backend Django/Gunicorn dans le service `backend`.
- Frontend React compilé puis servi par Nginx dans le service `frontend`.
- Healthchecks et dépendances : `db` doit être saine avant `backend`, puis `backend` doit répondre avant `frontend`.
- Le frontend relaie `/api/` vers le backend sur le réseau Docker interne.

## Démarrage complet avec Docker

Avant le démarrage, créer un fichier `.env` local à partir de `.env.example` et
remplacer tous les secrets et valeurs d'environnement. Ce fichier est
ignoré par Git et n'est jamais envoyé au dépôt.

Depuis la racine du projet, démarrer les trois services :

```powershell
docker compose up --build
```

Le backend attend PostgreSQL, applique les migrations, charge les utilisateurs de démonstration et lance Gunicorn. Le frontend est ensuite servi par Nginx.

URLs utiles :

- Frontend : http://localhost/
- API directe : http://localhost:8000/api/
- API via la passerelle : http://localhost/api/
- Documentation Swagger : http://localhost:8000/api/docs/
- Swagger via la passerelle : http://localhost/api/docs/
- Schéma OpenAPI : http://localhost:8000/api/schema/

Les paramètres sont centralisés dans `.env`. Les secrets destinés à Kubernetes
(`DJANGO_SECRET_KEY`, mots de passe, secret OAuth) doivent être stockés dans un
`Secret`; les URLs, hôtes, ports et chemins doivent être stockés dans un
`ConfigMap`. Le stockage local utilise `STORAGE_BACKEND` et peut être remplacé
par un backend S3 sans modifier les modèles ni le frontend.

Les logs backend sont émis en JSON sur stdout avec un identifiant de requête
`X-Request-ID`. Ils peuvent être collectés directement par Fluent Bit,
Elasticsearch/Kibana ou Datadog. Les variables `LOG_LEVEL`,
`LOG_SERVICE_NAME` et `LOG_ENVIRONMENT` contrôlent leur classification.

En local, les logs de tous les conteneurs sont stockés par Elasticsearch et
consultables dans Kibana. Fluent Bit collecte les logs Docker et les envoie
uniquement au service Elasticsearch local. Les données sont persistées dans le
volume Docker `elasticsearchdata`. Voir [logging/README.md](logging/README.md).

Vérifier les services :

```powershell
docker compose ps
```

Les trois services doivent apparaître avec le statut `healthy`.

## Authentification API

Exemple de connexion :

```powershell
$body = @{username='patient1'; password='DemoPass123!'} | ConvertTo-Json
$login = Invoke-RestMethod `
	-Uri http://localhost:8000/api/auth/login/ `
	-Method Post `
	-ContentType 'application/json' `
	-Body $body
```

Utiliser ensuite le token retourné dans l'en-tête :

```text
Authorization: Token <token>
```

Endpoints principaux :

- `GET /api/patients/`
- `GET /api/doctors/`
- `GET /api/appointments/`
- `GET /api/medical-records/`
- `POST /api/patients/{patient_id}/permissions/`
- `POST /api/patients/{patient_id}/permissions/{doctor_id}/revoke/`
- `GET /api/audit-logs/`

Comptes de démonstration créés par `python manage.py seed` :

- `patient1` à `patient5`
- `doctor1` à `doctor3`
- `admin`
- Mot de passe : `DemoPass123!`

## Structure du projet

```text
backend/       API Django REST, modèles, permissions et tests
frontend/      Application React/Vite et image Nginx
template-front/Exports HTML et références visuelles Stitch
docker-compose.yml
```

## Validation réalisée

- Build de l'image backend réussi.
- Build React/Vite réussi.
- Connexion backend vers PostgreSQL vérifiée.
- Authentification de `patient1` vérifiée.
- Appel d'une route protégée avec token vérifié.
- Frontend servi par Nginx avec HTTP 200.
- Proxy frontend vers Swagger backend vérifié avec HTTP 200.
- Healthchecks PostgreSQL, backend et frontend au vert.

## Limites actuelles

- Les écrans React utilisent encore des données mockées pour la démonstration visuelle.
- Le formulaire de connexion frontend doit encore être relié directement à `POST /api/auth/login/`.
- Le chiffrement AES, la Blockchain, l'IA, l'IoT et Kubernetes restent des extensions prévues par la roadmap.

Arrêter les services :

```powershell
docker compose down
```
