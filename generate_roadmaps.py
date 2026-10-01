from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).parent


def register_font():
    for path in (
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/calibri.ttf"),
        Path("C:/Windows/Fonts/DejaVuSans.ttf"),
    ):
        if path.exists():
            pdfmetrics.registerFont(TTFont("ProjectFont", str(path)))
            return "ProjectFont"
    return "Helvetica"


FONT = register_font()
PAGE_WIDTH, _ = A4


def make_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("ProjectTitle", parent=base["Title"], fontName=FONT, fontSize=24, leading=29, alignment=TA_CENTER, textColor=colors.HexColor("#123047"), spaceAfter=12),
        "subtitle": ParagraphStyle("Subtitle", parent=base["Normal"], fontName=FONT, fontSize=11, leading=16, alignment=TA_CENTER, textColor=colors.HexColor("#476273"), spaceAfter=18),
        "h1": ParagraphStyle("HeadingOne", parent=base["Heading1"], fontName=FONT, fontSize=17, leading=21, textColor=colors.HexColor("#123047"), spaceBefore=10, spaceAfter=8),
        "h2": ParagraphStyle("HeadingTwo", parent=base["Heading2"], fontName=FONT, fontSize=12, leading=15, textColor=colors.HexColor("#007c83"), spaceBefore=8, spaceAfter=5),
        "body": ParagraphStyle("Body", parent=base["BodyText"], fontName=FONT, fontSize=9.5, leading=14, textColor=colors.HexColor("#253746"), spaceAfter=5),
        "cell": ParagraphStyle("Cell", parent=base["BodyText"], fontName=FONT, fontSize=8.3, leading=11, textColor=colors.HexColor("#253746")),
        "cell_bold": ParagraphStyle("CellBold", parent=base["BodyText"], fontName=FONT, fontSize=8.5, leading=11, textColor=colors.HexColor("#123047")),
    }


S = make_styles()


def p(text, style="body"):
    return Paragraph(text, S[style])


def bullets(items):
    return [p("• " + item) for item in items]


def stage(number, title, objective, tasks, deliverables, validation):
    result = [p(f"Étape {number} - {title}", "h1"), p(f"<b>Objectif :</b> {objective}"), p("<b>Tâches :</b>")]
    result.extend(bullets(tasks))
    result.extend([p(f"<b>Livrables :</b> {deliverables}"), p(f"<b>Validation :</b> {validation}"), Spacer(1, 4 * mm)])
    return result


def overview(rows):
    data = [[p("Étape", "cell_bold"), p("But", "cell_bold"), p("Résultat attendu", "cell_bold")]]
    data.extend([[p(a, "cell"), p(b, "cell"), p(c, "cell")] for a, b, c in rows])
    table = Table(data, colWidths=[28 * mm, 65 * mm, 82 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d9eef0")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#a9c3c9")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#d9eef0"))
    canvas.line(18 * mm, 14 * mm, PAGE_WIDTH - 18 * mm, 14 * mm)
    canvas.setFont(FONT, 7.5)
    canvas.setFillColor(colors.HexColor("#6a7c86"))
    canvas.drawString(18 * mm, 9 * mm, "MedChain / SecureHealthOps - feuille de route de réalisation")
    canvas.drawRightString(PAGE_WIDTH - 18 * mm, 9 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build_pdf(filename, title, subtitle, summary, stages, final_checks):
    doc = SimpleDocTemplate(str(ROOT / filename), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=17 * mm, bottomMargin=20 * mm, title=title, author="MedChain project")
    story = [Spacer(1, 20 * mm), p(title, "title"), p(subtitle, "subtitle"), p("Synthèse du rapport", "h2"), p(summary), Spacer(1, 3 * mm), p("Vue d'ensemble des étapes", "h2")]
    story.extend([overview([(n, title_text, deliverables) for n, title_text, _, _, deliverables, _ in stages]), PageBreak()])
    for number, title_text, objective, tasks, deliverables, validation in stages:
        story.extend(stage(number, title_text, objective, tasks, deliverables, validation))
    story.extend([PageBreak(), p("Critères de fin du périmètre", "h1"), p("La partie est considérée comme prête lorsque les contrôles suivants sont démontrés :"), *bullets(final_checks), Spacer(1, 8 * mm), p("Ordre conseillé", "h2"), p("Terminer et tester chaque étape avant de commencer la suivante. Les étapes de sécurité et de qualité accompagnent le développement dès le premier endpoint ou écran." )])
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


BACKEND_STAGES = [
    ("1", "Stabiliser le socle actuel", "Rendre la base Django exécutable et reproductible.", ["Corriger la configuration et vérifier les variables d'environnement de la base de données.", "Vérifier migrations, administration, seed de données et démarrage avec Docker/PostgreSQL.", "Ajouter une configuration séparée développement/test et retirer les secrets codés en dur."], "Projet Django démarrable, migrations propres, données de démonstration reproductibles.", "Lancer les checks Django, les migrations et un appel aux trois endpoints existants."),
    ("2", "Modéliser le domaine médical", "Faire évoluer le CRUD minimal vers un modèle compatible avec le cahier des charges.", ["Relier les utilisateurs Django ou Keycloak aux profils Patient et Médecin.", "Ajouter dossiers/données médicales, observations, mesures IoT, permissions et statut de partage.", "Contraindre les dates, identifiants, relations et suppressions pour préserver la cohérence."], "Modèles, migrations, serializers et documentation de schéma versionnés.", "Créer un patient, un médecin, une donnée médicale et vérifier les relations par tests."),
    ("3", "Authentification et RBAC", "Protéger l'API conformément aux rôles Patient, Médecin, Administrateur et DevSecOps.", ["Intégrer Keycloak/OIDC ou une stratégie JWT documentée.", "Définir permissions par endpoint et filtrer les querysets côté serveur.", "Refuser par défaut les accès anonymes et retourner 401/403 de manière cohérente."], "Configuration IAM, permissions DRF, matrice des droits et endpoints protégés.", "Tester un accès patient, médecin et administrateur, notamment un cas 403."),
    ("4", "Partage et révocation", "Permettre au patient de garder le contrôle de ses données.", ["Créer les opérations d'autorisation ciblée par médecin et par type de donnée.", "Ajouter révocation, expiration éventuelle et contrôle effectif à chaque lecture.", "Prévoir l'historique des autorisations et des accès consultable par le patient."], "API de partage/révocation, règles métier et tests de non-régression.", "Rejouer les scénarios partage, accès non autorisé et révocation du rapport."),
    ("5", "Confidentialité et intégrité", "Protéger les données sensibles et détecter toute altération.", ["Chiffrer les champs sensibles avec AES-256 via une gestion de clés/secrets externe.", "Calculer un hash SHA-256 canonique des données et enregistrer la référence.", "Brancher un registre Blockchain de démonstration ou un adaptateur, puis générer une alerte en cas de mismatch."], "Service crypto, vérification d'intégrité, événements d'alerte et documentation des limites du prototype.", "Modifier une donnée en test et obtenir HASH MISMATCH puis un événement de sécurité."),
    ("6", "Audit, observabilité et API", "Rendre les opérations sensibles traçables et exploitables.", ["Journaliser authentification, lecture, écriture, partage, révocation et échec de permission.", "Ne jamais écrire de données médicales ou secrets dans les logs.", "Compléter Swagger/OpenAPI, health checks, métriques et gestion d'erreurs uniforme."], "AuditLog, événements de sécurité, endpoints documentés et métriques.", "Retrouver l'acteur, l'action, la cible, la date et le résultat d'une opération."),
    ("7", "IA expérimentale et IoT", "Ajouter les deux extensions prévues sans les confondre avec un diagnostic médical.", ["Exposer un service de prédiction indépendant basé sur un dataset de démonstration et ses métriques.", "Créer un simulateur IoT MQTT, valider les mesures, les associer au patient et les chiffrer.", "Versionner modèle, schéma des messages, seuils et avertissement 'expérimental'."], "API IA, simulateur MQTT, validation des messages et intégration au dossier.", "Recevoir une mesure simulée et obtenir une prédiction avec métriques documentées."),
    ("8", "Tests, conteneurs et DevSecOps", "Industrialiser la qualité et bloquer les artefacts dangereux.", ["Écrire tests unitaires, API, permissions, intégrité et scénarios métier complets.", "Finaliser Docker Compose puis préparer les manifests Kubernetes et secrets externes.", "Ajouter Gitleaks, Semgrep/Sonar, OWASP Dependency-Check ou Trivy, Checkov, tests et ZAP avec security gates."], "Pipeline CI/CD, images scannées, manifests, seuils justifiés et rapport de couverture.", "Faire échouer volontairement le pipeline avec un secret, une vulnérabilité et un test rouge."),
]


FRONTEND_STAGES = [
    ("1", "Cadrage UX et architecture", "Transformer les rôles et scénarios du rapport en parcours simples.", ["Définir les écrans par rôle : connexion, espace patient, espace médecin, administration et supervision.", "Décrire les parcours partage, révocation, consultation, accès refusé et alerte d'intégrité.", "Choisir une stack frontend et une structure par features, avec environnement API configurable."], "Carte des écrans, navigation, contrats API attendus et maquettes basse fidélité.", "Chaque exigence FR-01 à FR-12 possède un écran ou un état identifié."),
    ("2", "Design system sécurisé", "Installer une interface lisible et adaptée aux données de santé.", ["Définir typographie, couleurs d'état, grille, composants de formulaire, tableaux, badges et alertes.", "Prévoir responsive mobile/desktop, navigation clavier, contrastes et libellés accessibles.", "Différencier clairement information médicale, événement d'audit, succès, erreur et avertissement."], "Tokens UI, composants réutilisables, pages de chargement/erreur/vide et règles d'accessibilité.", "Valider les écrans sur mobile et desktop avec navigation clavier et contraste suffisant."),
    ("3", "Connexion et profils", "Connecter l'interface à l'IAM et afficher uniquement le contexte autorisé.", ["Implémenter login/logout, renouvellement de session et protection des routes.", "Charger le profil et le rôle, puis adapter menu, actions et redirections.", "Afficher des erreurs non sensibles et gérer expiration, chargement et absence de permissions."], "Flux d'authentification, garde de routes, store/session et profils patient/médecin.", "Un utilisateur non connecté est redirigé et aucun écran protégé ne révèle de données."),
    ("4", "Espace patient", "Donner au patient une vue claire de ses données et de leurs accès.", ["Afficher dossier, rendez-vous, mesures et résultats IA avec états de chargement fiables.", "Ajouter consultation/ajout de donnée de démonstration avec validation côté interface et serveur.", "Construire gestion des médecins autorisés, partage, révocation et historique des accès."], "Dashboard patient, formulaires, tableau des autorisations et historique.", "Le patient peut partager puis révoquer un médecin et voit l'état actualisé."),
    ("5", "Espace médecin", "Permettre au médecin de travailler uniquement sur les patients autorisés.", ["Afficher la liste filtrée des patients accessibles et leur niveau d'autorisation.", "Présenter données, observations et résultats IA sans exposer les patients non autorisés.", "Traiter les réponses 403 avec un message utile et sans contourner la sécurité backend."], "Dashboard médecin, fiche patient autorisée, formulaire d'observation et états d'accès.", "Un médecin ne voit pas un patient après révocation et reçoit un état d'accès explicite."),
    ("6", "Administration et supervision", "Rendre visibles la sécurité et l'exploitation du système.", ["Créer gestion des utilisateurs/rôles et consultation des journaux pour l'administrateur.", "Créer vues événements de sécurité, alertes d'intégrité, santé des services et métriques.", "Prévoir une vue DevSecOps pour pipelines, vulnérabilités, Kubernetes et résultats de scans."], "Écrans admin/DevSecOps avec tableaux filtrables, détail d'événement et indicateurs.", "Les écrans respectent les rôles et rendent visibles une alerte d'intégrité et un pipeline bloqué."),
    ("7", "IoT et IA côté interface", "Présenter les extensions expérimentales sans créer de confusion clinique.", ["Afficher mesures reçues, date, source, qualité et éventuelles anomalies.", "Afficher prédiction, métriques et avertissement clair : résultat expérimental, non diagnostic.", "Prévoir états réseau, données absentes, modèle indisponible et rafraîchissement contrôlé."], "Composants de mesures, graphique accessible, résultat IA et états de résilience.", "Une mesure simulée apparaît et une prédiction est affichée avec son contexte expérimental."),
    ("8", "Qualité, sécurité et livraison", "Livrer une interface fiable et cohérente avec le pipeline DevSecOps.", ["Ajouter tests composants, parcours E2E login/partage/révocation/403 et tests responsive.", "Éviter secrets dans le bundle, protéger XSS/CSRF selon le mode d'authentification et contrôler les dépendances.", "Conteneuriser le frontend, ajouter lint, tests, build, scan image et déploiement Kubernetes/GitOps."], "Build reproductible, tests automatisés, image scannée, manifests et documentation d'installation.", "Le pipeline bloque un test E2E rouge, un secret détecté ou une vulnérabilité critique."),
]


build_pdf("roadmap-backend.pdf", "Roadmap Backend - MedChain", "Découpage de réalisation basé sur le cahier des charges SecureHealthOps", "Le backend existant fournit déjà un socle Django REST avec les modèles Doctor, Patient et Appointment, leurs serializers, ViewSets, routes et Swagger. Il manque encore le lien avec les utilisateurs, les données médicales, le RBAC, le partage/révocation, le chiffrement, l'intégrité, l'audit, l'IA, l'IoT et la chaîne DevSecOps.", BACKEND_STAGES, ["Les scénarios de validation du rapport sont automatisés ou démontrés.", "Les rôles et permissions sont vérifiés côté serveur, jamais uniquement dans l'interface.", "Les données sensibles, secrets, logs et clés respectent la politique de sécurité définie.", "API, schémas, variables d'environnement, lancement Docker et limites du prototype sont documentés."])
build_pdf("roadmap-frontend.pdf", "Roadmap Frontend - MedChain", "Découpage de réalisation des parcours utilisateur et de la supervision", "Le rapport décrit quatre acteurs et des parcours centrés sur l'accès contrôlé aux données médicales. Le frontend doit donc être organisé par rôle, afficher des états de sécurité explicites et consommer une API protégée sans reproduire la logique d'autorisation côté navigateur.", FRONTEND_STAGES, ["Les parcours patient, médecin, administrateur et DevSecOps sont utilisables sur desktop et mobile.", "Toutes les routes protégées gèrent connexion, expiration, chargement, erreur et 403.", "Les parcours partage, révocation, audit, intégrité, IA et IoT sont testés de bout en bout.", "L'interface ne présente jamais le module IA comme un diagnostic médical."])
print("PDF generated: roadmap-backend.pdf, roadmap-frontend.pdf")