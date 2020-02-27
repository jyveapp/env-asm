env-asm
=======

``env-asm`` fetches a key/value secret from AWS secrets manager and updates
the existing environment before running a command.

If no secret name is present, return a list of all secret names the caller
has access to.

If no command is present, return the secret values.

Usage: ``env-asm <secret_name> <command_to_run>``

After :ref:`installation <installation>`, try it out by specifying a secret
and printing out the environment::

  env-asm my_secret_name env

If you need to run a command that takes command line flags, be sure to
prefix the entire command string like so::

  env-asm my_secret_name -- my-command --flag1 --flag2

Multiple secrets can be used by wrapping ``env-asm`` in other ``env-asm``
calls::

  env-asm secret1 env-asm secret2 command-name

List all secrets a caller has access to like so::

  env-asm

Retrieve the value of a secret by running::

  env-asm secret1