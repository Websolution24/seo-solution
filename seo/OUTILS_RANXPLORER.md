# Sources du pack Codex / Ranxplorer

Le pack regroupe 32 rôles et huit pôles avec des définitions natives Codex. Ce guide précise les sources, les outils de collecte et leurs limites.

## Connexion et limites

Le MCP officiel est `https://mcp.ranxplorer.com/mcp/ranxplorer`. Il utilise un compte Ranxplorer disposant d'un accès API, d'un token et de crédits. L'accès à l'interface d'un outil par un service tiers ne démontre pas cet accès API. La configuration exemple est inactive jusqu'à son activation par l'utilisateur.

Les noms ci-dessous sont les outils documentés le 15 octobre 2026. Vérifier ceux que la connexion expose réellement. Les données disponibles portent sur la base et les rapports Ranxplorer ; noter date, zone, unité et source. Une série estimée ne remplace pas les métriques privées Search Console/Analytics. Une difficulté SEO absente reste absente ; un indice de concurrence publicitaire ne la remplace pas.

Le MCP documenté ne fournit pas les clics/impressions/CTR Search Console du site. Le connecteur local décrit dans `seo/OUTILS_GSC.md` les récupère directement auprès de Google après autorisation, ainsi que les positions moyennes, les sitemaps et l'inspection d'URL. Les exports Search Console servent de secours si cette connexion manque.

La mesure des conversions Analytics, un relevé des réponses ChatGPT/Claude/Gemini, un crawl complet ou un backlink gap détaillé demandent des sources séparées. `get-backlinks-tool` est une synthèse, pas une liste exhaustive de liens et d'ancres. Les vérifications de contenu et techniques utilisent les fichiers, le navigateur ou les outils web réellement disponibles.

Ne pas modifier les protections du poste pour résoudre un problème de connexion. Ne pas lire, afficher ni consigner la clé : seule l'application de l'utilisateur la reçoit par variable d'environnement. Les appels API consomment des crédits ; le plafond autorisé est consigné dans seo/BUDGET_API.md ou dans le mandat humain.

## Correspondance des rôles

| Agent | Outils Ranxplorer utiles ou autres entrées |
|---|---|
| `seo-ancres` | Fichiers locaux / sources fournies / outils web disponibles |
| `seo-audit-global` | `get-seo-history-tool`, `get-seo-keywords-tool`, `get-seo-urls-tool`, `get-backlinks-tool` |
| `seo-brief` | `get-seo-serps-tool`, `get-keyword-paa-questions-tool` |
| `seo-cannibalisation` | Fichiers locaux / sources fournies / outils web disponibles |
| `seo-cartographe` | Fichiers locaux / sources fournies / outils web disponibles |
| `seo-chute-trafic` | `get-seo-history-tool`, `get-seo-evo-keywords-tool`, `get-seo-evo-urls-tool` |
| `seo-clusters` | `get-seo-keywords-tool`, `get-seo-urls-tool` |
| `seo-concurrents` | `get-seo-serps-tool`, `get-seo-competitors-tool`, `get-seo-keywords-tool`, `get-seo-urls-tool`, `get-backlinks-tool` |
| `seo-crawl` | Fichiers locaux / sources fournies / outils web disponibles |
| `seo-crawlers-ia` | Fichiers locaux / sources fournies / outils web disponibles |
| `seo-directeur` | Fichiers locaux / sources fournies / outils web disponibles |
| `seo-donnees-structurees` | Fichiers locaux / sources fournies / outils web disponibles |
| `seo-geo-visibilite` | Fichiers locaux / sources fournies / outils web disponibles |
| `seo-images-ux` | Fichiers locaux / sources fournies / outils web disponibles |
| `seo-indexation` | Fichiers locaux / sources fournies / outils web disponibles |
| `seo-intention` | `get-seo-serps-tool` |
| `seo-longue-traine` | `get-keyword-similars-tool`, `get-keyword-related-searches-tool`, `get-keyword-paa-questions-tool` |
| `seo-mise-a-jour` | `get-seo-serps-tool` |
| `seo-mots-cles-business` | `get-keyword-detail-tool`, `get-keyword-related-searches-tool`, `get-seo-keywords-tool` |
| `seo-opportunites-liens` | Fichiers locaux / sources fournies / outils web disponibles |
| `seo-outreach` | Fichiers locaux / sources fournies / outils web disponibles |
| `seo-performance` | Fichiers locaux / sources fournies / outils web disponibles |
| `seo-priorisation` | Fichiers locaux / sources fournies / outils web disponibles |
| `seo-profil-liens` | `get-backlinks-tool` |
| `seo-quick-wins` | `get-seo-keywords-tool`, `get-seo-opportunities-ct-tool`, `get-seo-serps-tool` |
| `seo-redacteur` | Fichiers locaux / sources fournies / outils web disponibles |
| `seo-relations-presse` | Fichiers locaux / sources fournies / outils web disponibles |
| `seo-relecteur-eeat` | Fichiers locaux / sources fournies / outils web disponibles |
| `seo-reporting` | Fichiers locaux / sources fournies / outils web disponibles |
| `seo-silos` | Fichiers locaux / sources fournies / outils web disponibles |
| `seo-structure-hn` | `get-seo-serps-tool` |
| `seo-title-meta` | Fichiers locaux / sources fournies / outils web disponibles |

## Sources techniques

- [MCP officiel Ranxplorer](https://mcp.ranxplorer.com/).
- [Packs API Ranxplorer](https://ranxplorer.com/packs-api).
- [Agents personnalisés Codex](https://learn.chatgpt.com/docs/agent-configuration/subagents).
- [Configuration MCP Codex](https://learn.chatgpt.com/docs/extend/mcp).

Consultation : 15 octobre 2026. La présence de fichiers de configuration ne prouve ni l'authentification ni une collecte réussie.
