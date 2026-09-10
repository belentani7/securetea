# Security Policy

## Reporting a Vulnerability

If you find a security vulnerability in SecureTea, please **do not open a public issue**.

Report it privately via:

- GitHub: https://github.com/belentani7/securetea/security/advisories/new
- Or contact the maintainer directly.

You should receive a response within 72 hours. Please include:

1. A clear description of the vulnerability
2. Steps to reproduce (proof of concept)
3. Affected versions/components
4. Any suggested fix

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| develop | :white_check_mark: |

## Security Model

- The web GUI and server backends are management tools and must be run on a
  trusted network or behind authentication + TLS.
- All secrets are configured via environment variables. Never commit real
  credentials to the repository.
- See `INFORME_DEBILIDADES_SECURETEA.md` (audit report) for the full security
  history and remediation list.
