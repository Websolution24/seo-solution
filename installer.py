"""Copy the public pack into a new local project. No network or account access."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tomllib

TOP_FILES = ['README.md', '.gitignore', 'LISEZ-MOI.md', 'WORKFLOWS.md', 'PROVENANCE.md', 'ADAPTATION.json',
             'INSTALLER.md', 'PROMPT_INSTALLATION.txt', 'installer.py', 'CONNECTER_SEARCH_CONSOLE.cmd', 'VERIFICATIONS.md']
SEO_FILES = ['CONTEXTE.md', 'OUTILS_RANXPLORER.md', 'OUTILS_GSC.md', 'BUDGET_API.md', 'donnees/LIRE-AVANT.md']
CONNECTOR_FILES = ['.gitignore', 'requirements.txt', 'gsc_client.py', 'gsc_auth.py', 'server.py',
                   'setup_connector.py', 'connecter_google.py', 'test_gsc.py']


def public_files(source: Path) -> list[Path]:
    manifest = json.loads((source/'ADAPTATION.json').read_text(encoding='utf-8'))
    names = [entry['agent'] for entry in manifest['agents']]
    if len(names) != 32 or len(set(names)) != 32 or any(not name.startswith('seo-') or any(c not in 'abcdefghijklmnopqrstuvwxyz-' for c in name) for name in names):
        raise ValueError('Le catalogue doit contenir exactement 32 noms de rôles valides.')
    paths = [Path(item) for item in TOP_FILES]
    paths += [Path('.codex/config.ranxplorer.example.toml')]
    paths += [Path('.codex/agents')/(name+'.toml') for name in names]
    paths += [Path('seo')/name for name in SEO_FILES]
    paths += [Path('connectors/google_search_console')/name for name in CONNECTOR_FILES]
    for relative in paths:
        current = source
        for part in relative.parts:
            current = current/part
            if current.is_symlink():
                raise ValueError('Un lien symbolique inattendu empêche la copie du pack.')
        path = source/relative
        if not path.is_file() or not path.resolve().is_relative_to(source.resolve()):
            raise ValueError('Un fichier nécessaire au pack est absent ou sort du dossier source.')
        if relative.suffix == '.toml':
            data = tomllib.loads(path.read_text(encoding='utf-8'))
            if relative.parent.name == 'agents' and (data.get('name') != relative.stem or not data.get('developer_instructions')):
                raise ValueError('Une définition d’agent est invalide.')
    return paths


def install(source: Path, destination: Path) -> dict:
    source = source.resolve()
    destination = destination.expanduser().resolve()
    if destination == source or destination.is_relative_to(source):
        raise ValueError('Choisis un dossier dédié extérieur au pack source.')
    if destination.exists():
        raise ValueError('Ce dossier existe déjà. Choisis un nouveau nom ; aucun fichier existant ne sera remplacé.')
    paths = public_files(source)
    destination.mkdir(parents=True, exist_ok=False)
    for relative in paths:
        origin, target = source/relative, destination/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origin, target)
        if hashlib.sha256(origin.read_bytes()).digest() != hashlib.sha256(target.read_bytes()).digest():
            raise OSError('Vérification de copie échouée ; le dossier partiel est conservé pour examen.')
    return {'folder_created':str(destination), 'files_verified':len(paths), 'agents_installed':32,
            'app_project_created':False, 'accounts_connected':False,
            'next_step':'Ajouter ce dossier comme projet local principal dans Work/Codex puis ouvrir un nouveau chat ; suivre les guides des connexions.'}


def main() -> int:
    parser = argparse.ArgumentParser(description='Installer les 32 agents dans un nouveau dossier de projet.')
    parser.add_argument('--destination', required=True, type=Path, help='Nouveau dossier de projet à créer ; il ne doit pas déjà exister.')
    args = parser.parse_args()
    try:
        print(json.dumps(install(Path(__file__).resolve().parent, args.destination), ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, KeyError, json.JSONDecodeError):
        print('Installation non terminée : vérifie le pack complet et choisis un nouveau dossier accessible extérieur au pack. Aucun réglage de compte ou projet existant n’a été remplacé.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
