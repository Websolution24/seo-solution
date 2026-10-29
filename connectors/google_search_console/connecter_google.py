"""User-run Google consent flow; no secret is passed to an agent or written in this pack."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from gsc_auth import CredentialVault, GoogleTransport, connect_google
from gsc_client import GSCClient, GSCError
from setup_connector import config_block, project_profile, register_config


def choose_client_file() -> Path:
    try:
        from tkinter import Tk, filedialog, TclError
    except ImportError:
        return choose_client_file_text()
    try:
        window = Tk()
        window.withdraw()
        try:
            selected = filedialog.askopenfilename(title='Choisir le fichier OAuth Google Application de bureau, conservé hors du pack', filetypes=[('Client OAuth Google', '*.json')])
        finally:
            window.destroy()
        if not selected:
            raise GSCError('Connexion annulée avant autorisation.')
        return Path(selected)
    except TclError:
        return choose_client_file_text()


def choose_client_file_text() -> Path:
    selected = input('Chemin du fichier OAuth Google Application de bureau, hors du pack : ').strip().strip('"')
    if not selected:
        raise GSCError('Connexion annulée.')
    return Path(selected)


def main() -> int:
    parser = argparse.ArgumentParser(description='Autoriser Search Console en lecture seule et choisir la propriété du projet.')
    parser.add_argument('--profil', help='Identifiant local non secret du profil ; ne pas saisir une clé ou un jeton.')
    args = parser.parse_args()
    folder = Path(__file__).resolve().parent
    root = folder.parents[1]
    try:
        profile = args.profil or project_profile(root)
        vault = CredentialVault(profile)
        print('Une fenêtre Google va demander uniquement la lecture de Search Console.')
        connect_google(choose_client_file(), vault)
        sites = GSCClient(GoogleTransport(vault)).list_sites()['sites']
        sites = [item for item in sites if item.get('permission_level') != 'siteUnverifiedUser']
        if not sites:
            raise GSCError('Google est autorisé, mais aucune propriété vérifiée n’est accessible avec ce compte.')
        print('Choisis la propriété du client pour ce projet :')
        for index, item in enumerate(sites, start=1):
            print(f"{index}. {item['site_url']}")
        choice = input('Numéro de la propriété : ').strip()
        if not choice.isdigit() or not 1 <= int(choice) <= len(sites):
            raise GSCError('Aucune propriété valide sélectionnée ; aucun serveur actif n’a été ajouté.')
        site_url = sites[int(choice)-1]['site_url']
        block = config_block(folder, profile, site_url, True)
        if register_config(root, block):
            print('Connexion vérifiée et serveur ajouté au projet. Rouvre le projet Codex pour charger ses outils.')
        else:
            # This file has no credential; it is a proposal, never a replacement of existing settings.
            proposal = root / '.codex/config.gsc.generated.toml'
            proposal.write_text(block, encoding='utf-8')
            print('Connexion Google vérifiée. Le serveur existant a été préservé : fusionne le bloc sans secret de .codex/config.gsc.generated.toml, puis rouvre le projet.')
        return 0
    except (GSCError, OSError) as error:
        print(str(error) if isinstance(error, GSCError) else 'Le fichier ou le dossier choisi est inaccessible.')
        return 1
    except (KeyboardInterrupt, EOFError):
        print('\nConnexion annulée.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
