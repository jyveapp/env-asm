import json
import os
import subprocess

import boto3
import pytest


@pytest.fixture
def secrets_manager_server(mocker):
    proc = subprocess.Popen(
        ['moto_server', 'secretsmanager', '-H', 'localhost', '-p', '5000'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    yield 'http://localhost:5000'
    proc.terminate()


def test_full_run(mocker, secrets_manager_server):
    """Tests a full CLI run with secrets.

    A fake boto server runs in the background. We set up fake secrets
    and then run the CLI directly to test it.
    """
    mocker.patch.dict(
        os.environ, {'AWS_SM_ENDPOINT_URL': secrets_manager_server}
    )

    conn = boto3.client(
        'secretsmanager',
        region_name='us-west-2',
        endpoint_url=secrets_manager_server,
    )

    conn.create_secret(
        Name='secret-name1',
        SecretString=json.dumps(
            {'env_var1': 'env_val1', 'env_var2': 'env_val2'}
        ),
    )
    conn.create_secret(
        Name='secret-name2',
        SecretString=json.dumps({'env_var2': 'overridden'}),
    )

    res = subprocess.run(
        'env-asm secret-name1 env',
        shell=True,
        check=True,
        stdout=subprocess.PIPE,
    )
    env_lines = res.stdout.decode().split('\n')
    assert 'env_var1=env_val1' in env_lines
    assert 'env_var2=env_val2' in env_lines

    res = subprocess.run(
        'env-asm secret-name1 env-asm secret-name2 env',
        shell=True,
        check=True,
        stdout=subprocess.PIPE,
    )
    env_lines = res.stdout.decode().split('\n')
    assert 'env_var1=env_val1' in env_lines
    assert 'env_var2=overridden' in env_lines
