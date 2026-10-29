# Connexion directe Google Search Console

Le pack comprend un connecteur local en lecture seule. Il récupère les mesures réelles de la propriété autorisée ; Ranxplorer conserve son rôle de source de données de marché et d'estimations.

## Activer une fois la connexion Google

1. Utilise Python 3.11 ou plus récent sur ton poste. Dans un projet Google Cloud à toi, active l'[API Search Console](https://console.cloud.google.com/apis/library/searchconsole.googleapis.com).
2. Configure le consentement OAuth et crée un client OAuth de type **Application de bureau**. Si ton application est en mode test, ajoute ton compte Google aux utilisateurs de test. Télécharge le fichier du client dans un dossier privé **extérieur à ce pack et au dépôt**. Ne le colle pas dans le chat et ne le joins pas au ZIP.
3. Sous Windows, double-clique sur `CONNECTER_SEARCH_CONSOLE.cmd`. Sinon, depuis le dossier du pack, lance `python connectors/google_search_console/setup_connector.py`.
4. Le programme installe ses bibliothèques localement, te fait choisir le fichier OAuth, puis ouvre la page officielle Google. Autorise uniquement la lecture Search Console et choisis le bon compte.
5. Choisis la propriété exacte du client dans la liste. Le programme ajoute le serveur local à `.codex/config.toml` sans remplacer les autres réglages. Si le même serveur existe déjà, il produit un bloc à fusionner, sans l'écraser.
6. Rouvre le projet Codex. Demande à l'agent de vérifier `gsc_connection_status` puis `gsc_list_sites` avant sa première collecte.

Le consentement Google est effectué par le propriétaire du compte. Les autorisations de session sont conservées dans le coffre du système (Windows Credential Manager, Trousseau macOS ou backend Linux sécurisé pris en charge), jamais dans ce pack. Aucun jeton n'est affiché dans les réponses aux agents. Le droit demandé est `webmasters.readonly` ; aucun outil n'envoie de sitemap, ne demande l'indexation, ni ne modifie une propriété. Si le coffre sécurisé manque, la connexion s'arrête sans créer un fichier de jeton en clair.

L'installation peut aussi se préparer sans connexion avec `python connectors/google_search_console/setup_connector.py --sans-connexion` ; le serveur reste alors inactif. Pour renouveler l'autorisation, relance le lanceur ou `connecter_google.py` avec le Python de l'environnement `.venv` du connecteur.

Chaque projet reçoit un profil local distinct. Après activation, `GSC_SITE_URL` limite les requêtes à la propriété sélectionnée. Ne retire pas cette limite pour changer silencieusement de client ; reconnecte le projet concerné.

## Outils exposés

| Outil | Utilisation |
|---|---|
| `gsc_connection_status` | Présence locale de l'autorisation, sans exposer de secret. Ne prouve pas un accès Google encore valide. |
| `gsc_list_sites` | Vérifier les propriétés accessibles et celle sélectionnée pour le projet. |
| `gsc_search_analytics` | Clics, impressions, CTR et position moyenne ; dimensions date, page, query, country, device ou searchAppearance ; filtres explicites. |
| `gsc_compare_periods` | Deux périodes de même durée, mêmes filtres et dimensions ; données retournées séparément. |
| `gsc_inspect_url` | État d'une URL connu de Google, sans soumission à l'indexation ni test en direct. |
| `gsc_list_sitemaps` | Lire les sitemaps connus de Search Console. |

Les dates sont inclusives et correspondent à l'heure du Pacifique utilisée par l'API. Les données de performance demandées sont finalisées. Le CTR est une fraction de 0 à 1 et la position une moyenne ; ne pas additionner les CTR, ni assimiler une position moyenne à une position fixe observée.

Une requête retourne au maximum 25 000 lignes. La pagination se demande explicitement avec `start_row` ; le connecteur ne lance pas une boucle de collecte illimitée. L'API ne garantit pas toutes les lignes et masque certaines requêtes : ne pas reconstituer un total de propriété en sommant arbitrairement ses requêtes. Les sources, périodes, filtres et limites sont transmis avec les résultats.

## Utilisation par les agents

Le directeur confirme la propriété. Les agents d'audit, mots-clés, longue traîne, cannibalisation, mise à jour, titles, gains rapides, baisse et reporting utilisent directement ces outils pour les mesures couvertes. L'agent indexation peut lire les sitemaps et inspecter les URL autorisées une à une.

Si la connexion manque ou Google refuse une propriété, les agents le disent ; ils n'inventent ni résultat ni connexion réussie. Les exports restent une solution de secours. Les conversions Analytics, réponses des IA et liens détaillés ne sont pas des données Search Console et conservent leurs sources séparées.

## Références officielles

- [Autorisation Search Console](https://developers.google.com/webmaster-tools/v1/how-tos/authorizing).
- [Requêtes Search Analytics](https://developers.google.com/webmaster-tools/v1/searchanalytics/query).
- [Liste des propriétés](https://developers.google.com/webmaster-tools/v1/sites/list).
- [Inspection d'URL](https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect).
- [Clients OAuth pour applications de bureau](https://developers.google.com/identity/protocols/oauth2/native-app).
- [Serveurs MCP dans Codex](https://learn.chatgpt.com/docs/extend/mcp).

L'activation du projet Google Cloud, la configuration de son consentement et l'autorisation du compte ne sont pas déjà effectuées par la présence de ces fichiers. Consultation des références : 15 octobre 2026.
