"""Google consent and OS-credential-vault integration; never serialize secrets to files."""
from __future__ import annotations

import json
import re
from pathlib import Path

from gsc_client import GSCError, SCOPE

SERVICE = 'equipe-seo-codex-google-search-console'
SAFE_BACKENDS = ('keyring.backends.Windows.', 'keyring.backends.macOS.',
                 'keyring.backends.SecretService.', 'keyring.backends.kwallet.')


def profile_name(profile: str) -> str:
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', profile):
        raise GSCError('Le profil doit contenir 1 à 64 lettres, chiffres, tirets ou underscores.')
    return profile


class CredentialVault:
    def __init__(self, profile: str = 'default'):
        import keyring
        self.profile = profile_name(profile)
        self.backend = keyring.get_keyring()
        backend_name = type(self.backend).__module__ + '.' + type(self.backend).__name__
        if not backend_name.startswith(SAFE_BACKENDS):
            raise GSCError('Aucun coffre système pris en charge. Configure Windows Credential Manager, le Trousseau macOS ou Secret Service/KWallet ; aucun fichier de jeton en clair ne sera créé.')

    def read(self) -> str | None:
        try:
            return self.backend.get_password(SERVICE, self.profile)
        except Exception:
            raise GSCError('Le coffre système est verrouillé ou indisponible.') from None

    def save(self, serialized_credentials: str) -> None:
        try:
            self.backend.set_password(SERVICE, self.profile, serialized_credentials)
        except Exception:
            raise GSCError('Impossible d’enregistrer la connexion dans le coffre système.') from None


def load_credentials(vault: CredentialVault):
    from google.oauth2.credentials import Credentials
    stored = vault.read()
    if not stored:
        raise GSCError('Connexion Google absente. Lance connecter_google.py pour autoriser la lecture Search Console.')
    try:
        credentials = Credentials.from_authorized_user_info(json.loads(stored), scopes=[SCOPE])
        if not credentials.has_scopes([SCOPE]):
            raise ValueError
    except (ValueError, TypeError, KeyError):
        raise GSCError('Connexion Google invalide. Relance connecter_google.py.') from None
    return credentials


def connect_google(client_file: Path, vault: CredentialVault) -> None:
    from google_auth_oauthlib.flow import InstalledAppFlow
    pack_root = Path(__file__).resolve().parents[2]
    client_file = client_file.expanduser().resolve()
    if client_file.is_relative_to(pack_root):
        raise GSCError('Conserve le fichier OAuth Google dans un dossier privé extérieur au pack et au dépôt.')
    if not client_file.is_file():
        raise GSCError('Le fichier OAuth Google choisi est introuvable.')
    try:
        flow = InstalledAppFlow.from_client_secrets_file(str(client_file), scopes=[SCOPE], autogenerate_code_verifier=True)
        credentials = flow.run_local_server(host='127.0.0.1', port=0, open_browser=True,
                                             authorization_prompt_message='Autorise la lecture Search Console dans la fenêtre Google ouverte.',
                                             success_message='Connexion autorisée. Tu peux fermer cette fenêtre.',
                                             access_type='offline', prompt='consent', timeout_seconds=300)
        if not credentials.has_scopes([SCOPE]):
            raise GSCError('Google n’a pas accordé le droit de lecture Search Console.')
        vault.save(credentials.to_json())
    except GSCError:
        raise
    except Exception:
        raise GSCError('Connexion Google non terminée. Vérifie le client OAuth de type Application de bureau, l’API activée et les comptes autorisés ; aucun secret n’a été affiché.') from None


class GoogleTransport:
    def __init__(self, vault: CredentialVault):
        from google.auth.transport.requests import AuthorizedSession
        self.vault = vault
        self.credentials = load_credentials(vault)
        self.session = AuthorizedSession(self.credentials)

    def __call__(self, method: str, url: str, **kwargs) -> dict:
        # Only the read endpoints constructed by GSCClient may be reached.
        base = 'https://www.googleapis.com/webmasters/v3/sites'
        if not (method == 'GET' and (url == base or re.fullmatch(re.escape(base) + r'/[^/?#]+/sitemaps', url))
                or method == 'POST' and re.fullmatch(re.escape(base) + r'/[^/?#]+/searchAnalytics/query', url)
                or method == 'POST' and url == 'https://searchconsole.googleapis.com/v1/urlInspection/index:inspect'):
            raise GSCError('Opération hors des fonctions de lecture autorisées.')
        try:
            response = self.session.request(method, url, timeout=45, allow_redirects=False, **kwargs)
        except Exception:
            raise GSCError('Google est injoignable ou la connexion doit être renouvelée ; aucun détail d’authentification n’est affiché.') from None
        if response.status_code == 401:
            raise GSCError('Connexion Google expirée ou révoquée. Relance connecter_google.py.')
        if response.status_code == 403:
            raise GSCError('Accès Google refusé : vérifie le droit sur cette propriété, l’API Search Console activée et les quotas.')
        if response.status_code == 429:
            raise GSCError('Quota Search Console atteint. Aucun nouvel essai automatique n’a été lancé.')
        if not 200 <= response.status_code < 300:
            raise GSCError(f'La lecture Google a échoué (HTTP {response.status_code}). Vérifie la propriété, la période et les paramètres.')
        try:
            result = response.json()
        except (ValueError, TypeError):
            raise GSCError('La réponse Google n’est pas un document JSON valide.') from None
        if not isinstance(result, dict):
            raise GSCError('Format de réponse Google inattendu.')
        # Save refreshed credentials only in the OS vault, never in tool output.
        self.vault.save(self.credentials.to_json())
        return result
