# MedChain Frontend

Application React/Vite de démonstration des interfaces MedChain.

## Démarrage

```powershell
cd frontend
npm install
npm run dev
```

L'application propose trois profils de démonstration : `Patient`, `Médecin` et `Administrateur`. Les données sont actuellement mockées pour présenter les parcours frontend avant le branchement complet à l'API Django.

Comptes affichés dans l'interface :

- `patient1`
- `doctor1`
- `admin`
- Mot de passe : `DemoPass123!`

## Structure

- `src/App.jsx` : shell, navigation, écrans et interactions de démonstration.
- `src/styles.css` : design system clinique et responsive.
- `src/main.jsx` : point d'entrée React.
- `../template-front/` : exports HTML et références visuelles Stitch originales.