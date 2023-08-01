#!/usr/bin/env python3
# Generate a new CSR
# https://cryptography.io/en/latest/x509/tutorial/
from __future__ import annotations
import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import toml

# sudo apt install python3-cryptography
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes


def generate_key(cfg: Config) -> Any:
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=cfg.key_size,
    )

def write_key(key, outpath: Path) -> None:
    keybytes = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    with outpath.open("wb") as f:
        f.write(keybytes)

def generate_csr(cfg: Config, key) -> Any:
    return x509.CertificateSigningRequestBuilder(
    ).subject_name(
        x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, cfg.common_name),
        ])
    ).add_extension(
        x509.SubjectAlternativeName(
            [x509.DNSName(name) for name in cfg.dns_names]
        ),
        critical=False,
    ).sign(key, hashes.SHA256())

def write_csr(csr, outpath: Path) -> None:
    with outpath.open("wb") as f:
        f.write(csr.public_bytes(serialization.Encoding.PEM))


@dataclass
class Config:
    hostname: str
    dns_names: list[str]

    @classmethod
    def load(cls, path: Path) -> Config:
        with path.open("r") as f:
            data = toml.load(f)

        return cls(
            hostname = data["hostname"],
            dns_names = data.get("dns_names") or [data["hostname"]],
        )

    @property
    def key_size(self) -> int:
        return 2048

    @property
    def common_name(self) -> str:
        return self.hostname

    @property
    def key_path(self) -> Path:
        return Path(self.hostname + ".key")

    @property
    def csr_path(self) -> Path:
        return Path(self.hostname + ".csr")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=Path)
    return parser.parse_args()

def main():
    args = parse_args()
    cfg = Config.load(args.config)

    key = generate_key(cfg)
    write_key(key, cfg.key_path)
    print(f"Key written to {cfg.key_path}")

    csr = generate_csr(cfg, key)
    write_csr(csr, cfg.csr_path)
    print(f"CSR written to {cfg.csr_path}")

if __name__ == '__main__':
    main()