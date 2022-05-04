# manage_vault_secrets

A python utility to assist in managing in-line Ansible-vaulted secrets in yaml files

This can be used for secrets in a yaml file where only the value of the secret is vaulted  
ex:

```yaml
foo: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  32313535363531303834373039343939663534316162343738323635653834633561643234383030
  6136653634353166376135303137613363656137613561660a323634343135633362666634353864
  33383933393865323036663034333266343539613564383364626166633838386639363065623864
  6264383630343730330a666532653766336332313435616238636330383937663531376436333336
  3635
```

This tool cannot be used for yaml where the entire file has been encrypted with Ansible-vault

## requirements

* python 3.10
* pyenv
* pipenv

## setup

Create a pipenv and activate env

* `pipenv install`
  * first time only, or when requirements are updated
* `pipenv shell`
  * must source env before use

## usage

### Commands

* add_update_secret
    * Adds/Updates Ansible vaulted secrets to a given yaml file
* read_secret
    * Decrypts Ansible vaulted secrets from a given yaml file and prints them to stdout
    * Multiple keys can be decrypted at once by specifying the `--key` option multiple times
* secret_from_file
    * Add/Updates an Ansible vaulted secret to a given yaml file from file input
    * Useful for when you want to add an RSA key or cert to a vault

See command help pages for more info. Ex: `python3 manage-vault-secrets.py read_secret --help`
