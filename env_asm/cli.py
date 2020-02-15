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


def fetch(secret_name):
    """
    Fetches a secret with a given secret ID.

    Assumes the secret is stored as a JSON dictionary and returns the result
    as a dictionary.
    """
    region_name = os.environ.get('AWS_DEFAULT_REGION', 'us-west-2')
    client = boto3.client(
        'secretsmanager',
        region_name=region_name,
        endpoint_url=os.environ.get('AWS_SM_ENDPOINT_URL'),
    )
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])


@click.command()
@click.argument('secret_name')
@click.argument('command', nargs=-1)
def main(secret_name, command):
    """
    Run a process with secrets from AWS Secrets Manager as environment variables.

    USAGE:

    ./env-asm [secret_name] -- [command] [...args]
    """
    if not command:
        raise click.ClickException(
            'Command was not provided. Please provide a command to execute.'
        )

    executable = spawn.find_executable(command[0])

    secrets = fetch(secret_name)

    update_env(secrets)

    os.execl(executable, *command)
