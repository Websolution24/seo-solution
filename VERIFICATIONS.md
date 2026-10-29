# Vérifications du pack — 15 octobre 2026

## Effectué

- Lecture et contrôle de l'archive source fournie avant adaptation : 34 fichiers Markdown, dont 32 rôles ; aucune instruction malveillante repérée, aucun script ou exécutable, aucun `AGENTS.md`. Ce constat porte sur les fichiers examinés.
- Validation des 32 fichiers TOML Codex et de leurs noms ; 13 rôles orientés vers la collecte directe Search Console pour les tâches couvertes.
- 24 tests hors ligne du connecteur : requêtes et filtres, périodes, limites de pagination, restriction de propriété, contrôle des domaines, endpoints de lecture, erreurs HTTP sans détail privé et préservation des configurations existantes.
- Essai réel du protocole MCP local sur Windows avec données fictives : initialisation, catalogue des six outils et annotations de lecture seule, statut sans autorisation, lecture des propriétés et des mesures fictives, refus d'une autre propriété. Aucun compte ni appel Google réel utilisé.
- Trois scénarios d'installation : copie des 32 rôles dans un dossier neuf avec vérification des fichiers, refus d'écraser un dossier existant, refus d'une copie imbriquée dans le pack source.
- Construction du ZIP depuis une liste explicite de fichiers publics. Les environnements Python, caches, configurations générées et fichiers d'autorisation ne sont pas inclus.

## À vérifier lors de la première activation

- Chargement effectif des 32 rôles dans un nouveau chat du projet cible ; les fichiers valides ne prouvent pas leur disponibilité dans toutes les versions de l'application.
- Consentement OAuth Google, accès à la propriété choisie et première lecture réelle. La préparation du pack n'a pas connecté de compte Google.
- Accès personnel API Ranxplorer, outils réellement exposés et budget autorisé. Aucun compte API réel n'a été testé.
- Création du projet dans l'interface Work, lorsque l'application expose cette fonction ; l'installateur crée et vérifie les fichiers, et indique honnêtement `app_project_created = false`.

Les tests utilisent uniquement des données fictives. Ils ne constituent pas une garantie d'absence de toute vulnérabilité, ni une preuve de résultat SEO.
