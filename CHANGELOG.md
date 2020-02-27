# Changelog
## 0.2.0 (2020-02-27)
### Feature
  - Add List Secrets Functionality [Will Chertoff, 500fea8]

    If no args are provided (i.e. ``env-asm``), list all the secrets the caller has access to see. If a secret is provided without a command (i.e. ``env-asm <secret_name>``, print the contents of the secret.

## 0.1.0 (2020-02-18)
### Feature
  - V1 Release [Will Chertoff, 62c955a]

    env-asm is a tool to launch a process with environment variables fetched from AWS Secrets Manager.
    Call ``env-asm <secret_name> <command>`` to run a command with key/value environment variables
    from the given secret.
### Trivial
  - Added tests and docs for V1 of env-asm. [Wes Kendall, 6306db6]

