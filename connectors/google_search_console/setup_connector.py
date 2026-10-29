"""Install locally and register this connector without changing other Codex settings."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tomllib
import subprocess
import sys
import venv

TOOLS = ['gsc_connection_status', 'gsc_list_sites', 'gsc_search_analytics',
         'gsc_compare_periods', 'gsc_inspect_url', 'gsc_list_sitemaps']


def project_profile(root: Path) -> str:
    return 'gsc-' + hashlib.sha256(str(root.resolve()).encode('utf-8')).hexdigest()[:12]


def python_path(folder: Path) -> Path:
    return folder / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')


def config_block(folder: Path, profile: str, site_url: str | None, enabled: bool) -> str:
    values = [('[mcp_servers.google_search_console]'),
              'command = ' + json.dumps(str(python_path(folder / '.venv').resolve())),
              'args = ' + json.dumps([str((folder / 'server.py').resolve())]),
              'enabled = ' + str(enabled).lower(),
              'startup_timeout_sec = 30',
              'enabled_tools = ' + json.dumps(TOOLS),
              '[mcp_servers.google_search_console.env]',
              'GSC_PROFILE = ' + json.dumps(profile)]
    if site_url:
        values.append('GSC_SITE_URL = ' + json.dumps(site_url))
    return '\n'.join(values) + '\n'


def register_config(root: Path, block: str) -> bool:
    target = root / '.codex/config.toml'
    existing = target.read_text(encoding='utf-8-sig') if target.exists() else ''
    # Never print existing configuration: it may contain private settings.
    try:
        parsed = tomllib.loads(existing)
    except tomllib.TOMLDecodeError:
        raise OSError('Configuration existante invalide ; aucun changement effectué.') from None
    if 'google_search_console' in parsed.get('mcp_servers', {}):
        return False
    tomllib.loads(existing + '\n' + block)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('a', encoding='utf-8', newline='\n') as handle:
        handle.write(('\n' if existing and not existing.endswith('\n') else '') + '\n' + block)
    return True


def install(folder: Path) -> Path:
    environment = folder / '.venv'
    interpreter = python_path(environment)
    if not interpreter.is_file():
        venv.EnvBuilder(with_pip=True, clear=False).create(environment)
    subprocess.run([str(interpreter), '-m', 'pip', 'install', '--disable-pip-version-check',
                    '-r', str(folder / 'requirements.txt')], check=True)
    return interpreter


def main() -> int:
    parser = argparse.ArgumentParser(description='Installer la connexion Search Console en lecture seule.')
    parser.add_argument('--sans-connexion', action='store_true', help='Installer et préparer le serveur inactif, sans ouvrir Google.')
    args = parser.parse_args()
    if sys.version_info < (3, 11):
        print('Python 3.11 ou plus récent est nécessaire.')
        return 1
    folder = Path(__file__).resolve().parent
    root = folder.parents[1]
    try:
        interpreter = install(folder)
        if not args.sans_connexion:
            # The interactive helper registers only after Google consent and property selection.
            return subprocess.run([str(interpreter), str(folder / 'connecter_google.py')]).returncode
        created = register_config(root, config_block(folder, project_profile(root), None, False))
        print('Serveur préparé mais inactif. Lance connecter_google.py pour autoriser Google.' if created
              else 'Un serveur google_search_console existe déjà ; sa configuration a été préservée.')
        return 0
    except (OSError, subprocess.CalledProcessError):
        print('Installation non terminée. Vérifie Python, la connexion réseau et les droits du dossier ; aucune autorisation Google n’a été obtenue.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
