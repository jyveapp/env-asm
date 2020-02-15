env-asm
=======

``env-asm`` fetches a key/value secret from AWS secrets manager and updates
the existing environment before running a command.

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
