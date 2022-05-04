from ruamel.yaml import YAML
from ansible.constants import DEFAULT_VAULT_ID_MATCH
from ansible.parsing.vault import VaultLib, VaultSecret
from typing import List
from os.path import exists
import typer
import logging

yaml=YAML() 
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
app = typer.Typer()

class VaultString:
  def __init__(self, string):
    self.string = string
  def __repr__(self):
    return self.string
  def decrypt(self, vault):
    return vault.decrypt(self.string).decode('utf-8')
  def update(self, vault, new_value):
    self.string = vault.encrypt(new_value).decode('utf-8')
    return


def vault_string_constructor(loader, node):
    return VaultString(loader.construct_scalar(node))


def vault_string_representer(dumper, data):
    return dumper.represent_scalar('!vault', str(data), style='|')


yaml.constructor.add_constructor('!vault', vault_string_constructor)
yaml.representer.add_representer(VaultString, vault_string_representer)


def get_vault(vault_pass):
    vault = VaultLib([(DEFAULT_VAULT_ID_MATCH, VaultSecret(vault_pass.encode()))])
    return vault


def _add_update_secret(vault_pass, key, vault_path, secret_value):
    vault = get_vault(vault_pass)
    vaultfile_exists = exists(vault_path)

    try:
        with open(vault_path, 'r') as v:
            vault_content = yaml.load(v) or {}
        vaultfile_exists = True
    except FileNotFoundError:
        vault_content = {}
        vaultfile_exists = False

    key_exists = key in vault_content
    vault_content.setdefault(key, VaultString('dummy')).update(vault, secret_value)

    with open(vault_path, 'w+') as v:
      yaml.dump(vault_content, v)

    if not vaultfile_exists:
      logging.info('New vault file created: %s', vault_path)

    if key_exists:
      logging.info('Value updated in %s for: %s', vault_path, key)
    else:
      logging.info('New secret added to %s for: %s', vault_path, key)


@app.command("read_secret")
def read_vault_secret(vault_pass: str = typer.Option(..., prompt=True, hide_input=True),
                      key: List[str] = typer.Option(...),
                      vault_path: str = typer.Option(...)):

    '''Decrypts Ansible vaulted secrets from a given yaml file and prints them to stdout.
    Multiple keys can be read at once by passing the --key option multiple times.'''

    vault = get_vault(vault_pass)

    with open(vault_path, 'r') as v:
      vault_content = yaml.load(v)

    for k in key:
        print(f'{k}: {vault_content[k].decrypt(vault)}')


@app.command("add_update_secret")
def add_update_vault_secret(vault_pass: str = typer.Option(..., prompt=True, confirmation_prompt=True, hide_input=True),
                        key: str = typer.Option(...),
                        vault_path: str = typer.Option(...),
                        new_value: str = typer.Option(..., prompt=True, confirmation_prompt=True, hide_input=True)):

    '''Adds/Updates Ansible vaulted secrets to a given yaml file'''

    _add_update_secret(vault_pass, key, vault_path, new_value)


@app.command("secret_from_file")
def secret_from_file(vault_pass: str = typer.Option(..., prompt=True, confirmation_prompt=True, hide_input=True),
                  key: str = typer.Option(...),
                  vault_path: str = typer.Option(...),
                  file_path: str = typer.Option(..., prompt=True, confirmation_prompt=True, hide_input=True)):

    '''Add/Updates an Ansible vaulted secret to a given yaml file from file input.
    Useful for when you want to add an RSA key or cert to a vault.'''

    with open(file_path, 'r') as f:
      secret_value = f.read()

    _add_update_secret(vault_pass, key, vault_path, secret_value)


if __name__ == "__main__":
    app()
