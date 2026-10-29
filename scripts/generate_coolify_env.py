"""Generate a private deployment env file; SMTP values must be completed before deploying."""

import argparse
import base64
import secrets
from pathlib import Path
from urllib.parse import urlparse


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="URL pública HTTPS, sin puerto interno de Coolify.")
    parser.add_argument("--year", type=int, default=2027)
    parser.add_argument("--output", type=Path, default=Path(".env.coolify"))
    args = parser.parse_args()
    parsed = urlparse(args.url)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
    ):
        parser.error("--url debe ser una URL HTTPS sin ruta, parámetros ni fragmento.")
    if not 2000 <= args.year <= 2100:
        parser.error("--year debe estar entre 2000 y 2100.")
    values = {
        "PUBLIC_URL": args.url.rstrip("/"),
        "APPLICATION_YEAR": str(args.year),
        "SECRET_KEY": secrets.token_urlsafe(48),
        "JWT_SECRET_KEY": secrets.token_urlsafe(48),
        "DATA_ENCRYPTION_KEY": base64.urlsafe_b64encode(secrets.token_bytes(32)).decode(),
        "FILE_ENCRYPTION_KEY": base64.urlsafe_b64encode(secrets.token_bytes(32)).decode(),
        "DB_PASSWORD": secrets.token_urlsafe(36),
        "DB_ROOT_PASSWORD": secrets.token_urlsafe(36),
        "MINIO_ROOT_USER": secrets.token_hex(12),
        "MINIO_ROOT_PASSWORD": secrets.token_urlsafe(36),
        "MINIO_APP_ACCESS_KEY": secrets.token_hex(12),
        "MINIO_APP_SECRET_KEY": secrets.token_urlsafe(36),
    }
    template = (Path(__file__).resolve().parents[1] / ".env.coolify.example").read_text(encoding="utf-8")
    content = (
        "\n".join(
            f"{line.split('=', 1)[0]}={values.get(line.split('=', 1)[0], line.split('=', 1)[1])}"
            if "=" in line
            else line
            for line in template.splitlines()
        )
        + "\n"
    )
    with args.output.open("x", encoding="utf-8", newline="\n") as output:
        output.write(content)
    print(
        f"Archivo creado: {args.output}. Completá SMTP y cargá estas variables en Coolify. "
        'No se sobrescriben archivos existentes.'
    )


if __name__ == "__main__":
    main()
