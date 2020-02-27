'''
Populate the current process environment with secrets from AWS Secrets manager.

Replace this process with a given process with the current process environment
'''
from distutils import spawn
import json
import os

import boto3
import click


def update_env(vals):  # pragma: no cover
    os.environ.update(vals)


def _client():
    """
    Returns a secretsmanager boto client.
    """
    region_name = os.environ.get('AWS_DEFAULT_REGION', 'us-west-2')
    return boto3.client(
        'secretsmanager',
        region_name=region_name,
        endpoint_url=os.environ.get('AWS_SM_ENDPOINT_URL'),
    )


def _fetch(secret_name):
    """
    Fetches a secret with a given secret ID.

    Assumes the secret is stored as a JSON dictionary and returns the result
    as a dictionary.
    """
    response = _client().get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])


def _list():
    """
    List all ASM secrets by name a caller user has access to

    Returns a Dict { 'SecretList': [...] }
    """
    return _client().list_secrets().get('SecretList', [])


@click.command()
@click.argument('secret_name', required=False)
@click.argument('command', nargs=-1)
def main(secret_name, command):
    """
    Run a process with secrets from AWS Secrets Manager as environment variables.

    If no secret name is present, return a list of all secret names the caller
    has access to.

    If no command is present, return the secret values.

    USAGE:

    ./env-asm [secret_name] -- [command] [...args]
    """
    if not secret_name:
        for secret in _list():
            click.echo(secret['Name'])
        return

    if not command:
        click.echo(json.dumps(_fetch(secret_name)))
        return

    executable = spawn.find_executable(command[0])

    secrets = _fetch(secret_name)

    update_env(secrets)

    os.execl(executable, *command)
