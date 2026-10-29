# SEO Solution — Codex / Ranxplorer / Search Console

32 agents, huit pôles, un directeur. Ce pack utilise les définitions d’agents Codex, le MCP officiel Ranxplorer pour les collectes de marché et un connecteur Google Search Console en lecture seule pour les mesures du site.

## Installer dans un projet distinct

Pour une installation guidée par Work, joins le ZIP et colle `PROMPT_INSTALLATION.txt`. `INSTALLER.md` décrit le parcours ; `installer.py` crée un dossier neuf avec les 32 agents, sans écraser un projet. L'ajout de ce dossier à la liste des projets dépend des fonctions disponibles dans l'application et peut demander de le sélectionner une fois.

1. Décompresse le ZIP dans un nouveau dossier de projet. Le dossier caché `.codex/agents/` contient les 32 définitions natives. Si tu installes dans un projet existant, compare les fichiers avant de les fusionner ; ne remplace pas sa configuration ni ses instructions.
2. Ouvre ce dossier comme projet dans Codex. Les agents héritent de ton modèle et de tes permissions ; aucun modèle ni abonnement OpenAI précis n'est imposé par le pack.
3. Remplis `seo/CONTEXTE.md`. Le fichier de contexte d'origine est conservé. Pour Search Console, suis `seo/OUTILS_GSC.md` : prépare ton client OAuth Google de type Application de bureau, puis lance `CONNECTER_SEARCH_CONSOLE.cmd` sous Windows. Tu autorises la lecture dans Google et choisis la propriété du projet. Python 3.11 ou plus récent est nécessaire. Les autorisations restent dans le coffre du système ; aucun secret n'est à fournir à l'agent.
4. Pour la connexion directe, utilise ton propre accès API Ranxplorer et des crédits. Configure personnellement la variable d'environnement `RANXPLORER_API_KEY` dans l'environnement de l'application Codex, hors des fichiers du projet. Ne colle jamais la clé dans un chat, ce ZIP ou un dépôt.
5. Fusionne le bloc de `.codex/config.ranxplorer.example.toml` dans la configuration `.codex/config.toml` de ce projet, puis passe `enabled` à `true` lorsque la variable est configurée. L'exemple seul n'est pas chargé comme connexion active. Si un bloc `ranxplorer` existe déjà, adapte-le au lieu d'en créer un second.
6. Rouvre le projet ou ouvre un nouveau chat pour charger les rôles et les connexions. Vérifie les noms des agents et l'état des serveurs dans les outils proposés par Codex. Demande `gsc_connection_status` puis `gsc_list_sites` pour contrôler Search Console. Les essais du pack utilisent des données fictives ; aucun compte Google ni compte API Ranxplorer réel n'a été connecté lors de sa préparation.
7. Autorise un plafond d'appels/crédits dans le mandat ou dans `seo/BUDGET_API.md` avant les collectes payantes. Les tâches locales restent possibles avec les exports fournis.

## Premier lancement

> Utilise seo-directeur pour faire le point sur mon site et me proposer les trois actions de la semaine. Vérifie la propriété Search Console connectée, les sources disponibles et le budget API Ranxplorer autorisé. Lance les agents nécessaires, attends leurs retours et montre-moi le plan avant toute action sur le site.

Les 32 rôles sont un catalogue de spécialistes, pas 32 agents à lancer en même temps. Le directeur respecte les places disponibles dans Codex et donne un fichier distinct à chaque lot. Un agent n'est présenté comme exécuté que si son lancement a réussi. Les autres enchaînements sont dans `WORKFLOWS.md`.

## Ce qui demande des données supplémentaires

Les clics, impressions, CTR et positions moyennes du site viennent directement de Search Console après activation du connecteur. Les agents peuvent aussi lire les sitemaps et inspecter l'état connu d'une URL. Si la connexion n'est pas disponible, les exports Search Console restent utilisables.

Les conversions Analytics, réponses des moteurs IA, rapports complets de couverture d'indexation et listes détaillées de backlinks demandent leurs propres sources ou exports selon la mission. Aucune de ces données n'est inventée à partir de Ranxplorer. `seo/OUTILS_RANXPLORER.md` et `seo/OUTILS_GSC.md` précisent les capacités et limites.

Aucune publication, suppression, prise de contact ou dépense sans l'autorisation humaine prévue. Le pack produit des analyses et brouillons locaux.

## Les huit pôles d'origine

- Stratégie et audit : seo-directeur, seo-audit-global, seo-concurrents, seo-priorisation
- Recherche de mots-clés : seo-mots-cles-business, seo-longue-traine, seo-intention, seo-clusters
- Rédaction d'articles : seo-brief, seo-redacteur, seo-relecteur-eeat, seo-mise-a-jour
- Optimisation on-page : seo-title-meta, seo-structure-hn, seo-donnees-structurees, seo-images-ux
- Maillage interne : seo-cartographe, seo-silos, seo-ancres, seo-cannibalisation
- Technique et indexation : seo-indexation, seo-crawl, seo-performance, seo-crawlers-ia
- Analyse et croissance : seo-reporting, seo-quick-wins, seo-chute-trafic, seo-geo-visibilite
- Netlinking : seo-profil-liens, seo-opportunites-liens, seo-outreach, seo-relations-presse

## Version du pack

Configuration Codex et connecteurs : WebSolution24. Voir `PROVENANCE.md` pour le périmètre technique de cette version.
