"""Read-only Search Console operations, with an injectable HTTP transport."""
from __future__ import annotations

from datetime import date, datetime, timezone
import re
from typing import Any, Callable
from urllib.parse import quote, urlsplit

SCOPE = 'https://www.googleapis.com/auth/webmasters.readonly'
BASE = 'https://www.googleapis.com/webmasters/v3'
INSPECTION = 'https://searchconsole.googleapis.com/v1/urlInspection/index:inspect'
DIMENSIONS = {'date', 'query', 'page', 'country', 'device', 'searchAppearance'}
FILTER_DIMENSIONS = DIMENSIONS - {'date'}
OPERATORS = {'contains', 'equals', 'notContains', 'notEquals', 'includingRegex', 'excludingRegex'}
SEARCH_TYPES = {'web', 'image', 'video', 'news', 'discover', 'googleNews'}


class GSCError(Exception):
    """An actionable message which never contains credentials or raw HTTP errors."""


def validate_site(site_url: str) -> str:
    if not isinstance(site_url, str) or not site_url or len(site_url) > 4096:
        raise GSCError('Indique la propriété exacte affichée dans Search Console.')
    if site_url.startswith('sc-domain:'):
        host = site_url[len('sc-domain:'):]
        if not re.fullmatch(r'[A-Za-z0-9.-]+', host) or '..' in host or not host.strip('.'):
            raise GSCError('Propriété de domaine invalide ; exemple : sc-domain:example.com.')
    else:
        parsed = urlsplit(site_url)
        if parsed.scheme not in {'http', 'https'} or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise GSCError('La propriété URL doit être une URL HTTP(S) exacte, sans identifiant ni paramètres.')
    return site_url


def validate_dates(start_date: str, end_date: str) -> tuple[date, date]:
    try:
        if not all(isinstance(x, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', x) for x in (start_date, end_date)):
            raise ValueError
        start, end = date.fromisoformat(start_date), date.fromisoformat(end_date)
        if start > end:
            raise ValueError
    except (ValueError, TypeError):
        raise GSCError('Utilise une période inclusive valide au format AAAA-MM-JJ.') from None
    return start, end


def build_query(start_date: str, end_date: str, dimensions: list[str] | None = None,
                filters: list[dict[str, str]] | None = None, search_type: str = 'web',
                row_limit: int = 1000, start_row: int = 0) -> dict[str, Any]:
    validate_dates(start_date, end_date)
    dims = [] if dimensions is None else dimensions
    if not isinstance(dims, list) or any(not isinstance(x, str) or x not in DIMENSIONS for x in dims) or len(set(dims)) != len(dims):
        raise GSCError('Dimensions invalides ou répétées : date, query, page, country, device, searchAppearance.')
    if search_type not in SEARCH_TYPES:
        raise GSCError('Type de recherche invalide.')
    if type(row_limit) is not int or not 1 <= row_limit <= 25000 or type(start_row) is not int or start_row < 0:
        raise GSCError('row_limit doit être compris entre 1 et 25000 ; start_row doit être positif ou nul.')
    body: dict[str, Any] = {'startDate': start_date, 'endDate': end_date, 'dimensions': dims,
                            'type': search_type, 'rowLimit': row_limit, 'startRow': start_row,
                            'dataState': 'final', 'aggregationType': 'auto'}
    if filters is not None:
        if not isinstance(filters, list) or len(filters) > 20:
            raise GSCError('Les filtres doivent être une liste de vingt filtres maximum.')
        clean = []
        for item in filters:
            if not isinstance(item, dict) or set(item) - {'dimension', 'operator', 'expression'}:
                raise GSCError('Chaque filtre contient dimension, operator et expression uniquement.')
            dimension, operator, expression = item.get('dimension'), item.get('operator', 'equals'), item.get('expression')
            if dimension not in FILTER_DIMENSIONS or operator not in OPERATORS or not isinstance(expression, str) or not expression or len(expression) > 4096:
                raise GSCError('Filtre Search Console invalide.')
            clean.append({'dimension': dimension, 'operator': operator, 'expression': expression})
        if clean:
            body['dimensionFilterGroups'] = [{'groupType': 'and', 'filters': clean}]
    return body


class GSCClient:
    def __init__(self, request: Callable[..., dict[str, Any]], allowed_site: str | None = None):
        self.request = request
        self.allowed_site = validate_site(allowed_site) if allowed_site else None

    def _site(self, site_url: str) -> str:
        validate_site(site_url)
        if self.allowed_site and site_url != self.allowed_site:
            raise GSCError('Cette connexion est limitée à la propriété sélectionnée ; ne change pas de client implicitement.')
        return quote(site_url, safe='')

    def list_sites(self) -> dict[str, Any]:
        data = self.request('GET', BASE + '/sites')
        entries = data.get('siteEntry', [])
        if self.allowed_site:
            entries = [item for item in entries if item.get('siteUrl') == self.allowed_site]
        return {'source': 'Google Search Console API',
                'sites': [{'site_url': x.get('siteUrl'), 'permission_level': x.get('permissionLevel')} for x in entries],
                'selected_property': self.allowed_site,
                'note': 'Choisir la propriété exacte du client avant de collecter ses données.'}

    def search_analytics(self, site_url: str, start_date: str, end_date: str,
                         dimensions: list[str] | None = None, filters: list[dict[str, str]] | None = None,
                         search_type: str = 'web', row_limit: int = 1000, start_row: int = 0) -> dict[str, Any]:
        encoded = self._site(site_url)
        body = build_query(start_date, end_date, dimensions, filters, search_type, row_limit, start_row)
        data = self.request('POST', f'{BASE}/sites/{encoded}/searchAnalytics/query', json=body)
        rows = data.get('rows', [])
        return {'source': 'Google Search Console API', 'site_url': site_url,
                'collected_at': datetime.now(timezone.utc).isoformat(),
                'period': {'start_date': start_date, 'end_date': end_date, 'inclusive': True, 'timezone': 'America/Los_Angeles'},
                'dimensions': body['dimensions'], 'filters': body.get('dimensionFilterGroups', []),
                'search_type': search_type, 'data_state': 'final',
                'response_aggregation_type': data.get('responseAggregationType'),
                'rows': rows, 'row_count': len(rows), 'start_row': start_row, 'row_limit': row_limit,
                'next_start_row': start_row + len(rows) if len(rows) == row_limit else None,
                'limitations': ['Les lignes retournées par Google ne sont pas garanties exhaustives.',
                                'Les requêtes anonymisées et limites de l’API peuvent créer un écart avec les totaux.',
                                'CTR exprimé de 0 à 1 ; position moyenne observée, pas une position SERP fixe.',
                                'Ne pas sommer des CTR ou moyenner les positions de lignes pour reconstituer un total.']}

    def compare_periods(self, site_url: str, start_date: str, end_date: str,
                        comparison_start_date: str, comparison_end_date: str,
                        dimensions: list[str] | None = None, filters: list[dict[str, str]] | None = None,
                        search_type: str = 'web', row_limit: int = 1000) -> dict[str, Any]:
        current = validate_dates(start_date, end_date)
        previous = validate_dates(comparison_start_date, comparison_end_date)
        if current[1] - current[0] != previous[1] - previous[0]:
            raise GSCError('La comparaison exige deux périodes de même durée inclusive.')
        # Validate every argument before the first API call.
        self._site(site_url)
        build_query(start_date, end_date, dimensions, filters, search_type, row_limit)
        build_query(comparison_start_date, comparison_end_date, dimensions, filters, search_type, row_limit)
        return {'source': 'Google Search Console API',
                'current': self.search_analytics(site_url, start_date, end_date, dimensions, filters, search_type, row_limit),
                'comparison': self.search_analytics(site_url, comparison_start_date, comparison_end_date, dimensions, filters, search_type, row_limit),
                'note': 'Mêmes dimensions, filtres, type et durée. Les séries sont conservées séparément ; une ligne absente ne vaut pas automatiquement zéro.'}

    def inspect_url(self, site_url: str, inspection_url: str, language_code: str = 'fr-FR') -> dict[str, Any]:
        self._site(site_url)
        parsed = urlsplit(inspection_url)
        if parsed.scheme not in {'http', 'https'} or not parsed.hostname or parsed.username or parsed.password:
            raise GSCError('URL à inspecter invalide.')
        if site_url.startswith('sc-domain:'):
            domain = site_url[len('sc-domain:'):].lower().rstrip('.')
            host = parsed.hostname.lower().rstrip('.')
            belongs = host == domain or host.endswith('.' + domain)
        else:
            property_url = urlsplit(site_url)
            belongs = (parsed.scheme == property_url.scheme
                       and parsed.netloc.lower() == property_url.netloc.lower()
                       and parsed.path.startswith(property_url.path or '/'))
        if not belongs:
            raise GSCError('L’URL à inspecter doit appartenir à la propriété sélectionnée.')
        if not re.fullmatch(r'[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*', language_code):
            raise GSCError('Code de langue invalide.')
        data = self.request('POST', INSPECTION, json={'inspectionUrl': inspection_url, 'siteUrl': site_url, 'languageCode': language_code})
        return {'source': 'Google Search Console URL Inspection API', 'site_url': site_url,
                'inspection_url': inspection_url, 'inspection_result': data.get('inspectionResult', {}),
                'note': 'État connu de Google ; ce contrôle ne soumet pas l’URL à l’indexation et n’est pas un test en direct.'}

    def list_sitemaps(self, site_url: str) -> dict[str, Any]:
        encoded = self._site(site_url)
        data = self.request('GET', f'{BASE}/sites/{encoded}/sitemaps')
        return {'source': 'Google Search Console API', 'site_url': site_url, 'sitemaps': data.get('sitemap', [])}
