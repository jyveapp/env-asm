import json
import sys

import boto3
import moto
import pytest

from env_asm import cli


@pytest.fixture
def mock_exit(mocker):
    yield mocker.patch('sys.exit', autospec=True)


@pytest.fixture
def mock_successful_exit(mock_exit):
    yield
    mock_exit.assert_called_once_with(0)


@moto.mock_secretsmanager
@pytest.mark.usefixtures('mock_successful_exit')
def test_main(mocker):
    conn = boto3.client('secretsmanager', region_name='us-west-2')

    conn.create_secret(
        Name='secret-name1',
        SecretString=json.dumps(
            {'env_var1': 'env_val1', 'env_var2': 'env_val2'}
        ),
    )
    mocker.patch.object(sys, 'argv', ['env-asm', 'secret-name1', 'env'])
    exec_patch = mocker.patch('os.execl', autospec=True)
    env_patch = mocker.patch('env_asm.cli.update_env', autospec=True)
    cli.main()

    env_patch.assert_called_once_with(
        {'env_var1': 'env_val1', 'env_var2': 'env_val2'}
    )
    exec_patch.assert_called_once_with('/usr/bin/env', 'env')


@moto.mock_secretsmanager
@pytest.mark.usefixtures('mock_successful_exit')
def test_main_wo_command(mocker, capsys):
    conn = boto3.client('secretsmanager', region_name='us-west-2')

    conn.create_secret(
        Name='secret-name1',
        SecretString=json.dumps(
            {'env_var1': 'env_val1', 'env_var2': 'env_val2'}
        ),
    )
    mocker.patch.object(sys, 'argv', ['env-asm', 'secret-name1'])
    cli.main()
    captured_stdout = capsys.readouterr()
    assert (
        captured_stdout.out
        == '{"env_var1": "env_val1", "env_var2": "env_val2"}\n'
    )


@moto.mock_secretsmanager
@pytest.mark.usefixtures('mock_successful_exit')
def test_main_wo_secret_name(mocker, capsys):
    conn = boto3.client('secretsmanager', region_name='us-west-2')

    conn.create_secret(
        Name='secret-name1',
        SecretString=json.dumps(
            {'env_var1': 'env_val1', 'env_var2': 'env_val2'}
        ),
    )
    mocker.patch.object(sys, 'argv', ['env-asm'])
    cli.main()
    captured_stdout = capsys.readouterr()
    assert captured_stdout.out == 'secret-name1\n'
