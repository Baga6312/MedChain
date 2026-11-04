# MedChain mobile client

This is a Flutter/Dart-only client scaffold for the existing MedChain backend.
Flutter is intentionally not installed or executed by this change.

The client implements only:

- email/password registration;
- email/password login;
- session-token storage;
- authenticated `GET /api/auth/me/`;
- logout.

The mobile app communicates with Django through the API. It must never connect
directly to PostgreSQL or Redis; Redis remains an internal backend cache.

## Backend URL

The default Android emulator URL is:

```text
http://10.0.2.2:8000/api
```

Override it per environment without editing Dart source:

```powershell
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000/api
```

For Google Sign-In, use the Web OAuth client ID as the backend
`GOOGLE_OAUTH_CLIENT_ID` and pass the same value to Flutter:

```powershell
flutter run -d <device> `
  --dart-define=API_BASE_URL=http://192.168.100.37:8000/api `
  --dart-define=GOOGLE_SERVER_CLIENT_ID=<web-client-id>
```

In Google Cloud Console, enable the Google Identity API, configure the OAuth
consent screen, and create an Android OAuth client for the app's package name
and SHA-1 signing certificate. The Android client is used by Google Sign-In;
the Web client ID is the server client ID sent to the backend.

## Short development command

The repository includes a PowerShell launcher that reads
`GOOGLE_OAUTH_CLIENT_ID` and `MOBILE_API_BASE_URL` from the root `.env`:

```powershell
.\mobile\run-dev.ps1 -Device adb-R58M92F2MGX-L7U0Od._adb-tls-connect._tcp
```

For a physical phone, set `MOBILE_API_BASE_URL` in `.env` to the computer's
LAN address, for example `http://192.168.100.37:8000/api`.
