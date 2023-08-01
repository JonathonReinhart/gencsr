#!/usr/bin/env python3

# Copyright 2023 Google, LLC
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Generate a new CSR
# https://cryptography.io/en/latest/x509/tutorial/
from __future__ import annotations
import argparse
from dataclasses import dataclass
import importlib.metadata
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
    _dns_names: list[str]

    @classmethod
    def load(cls, path: Path) -> Config:
        with path.open("r") as f:
            data = toml.load(f)

        return cls(
            hostname = data["hostname"],
            _dns_names = data.get("dns_names", []),
        )

    @property
    def dns_names(self) -> list[str]:
        return [self.hostname, *self._dns_names]

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

def get_version() -> str:
    try:
        return importlib.metadata.version("gencsr")
    except importlib.metadata.PackageNotFoundError:
        return "???"

def parse_args() -> Config:
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="version",
            version="gencsr v" + get_version())

    parser.add_argument("--config", type=Path)

    parser.add_argument("--hostname")
    parser.add_argument("--dns-name", action="append", default=[])

    args = parser.parse_args()

    if args.config:
        if args.hostname or args.dns_name:
            parser.error("--config cannot be used with other options")
        return Config.load(args.config)

    if not args.hostname:
        parser.error("--hostname required (if --config is not used)")

    return Config(
        hostname = args.hostname,
        _dns_names = args.dns_name,
    )

def main():
    cfg = parse_args()

    key = generate_key(cfg)
    write_key(key, cfg.key_path)
    print(f"Key written to {cfg.key_path}")

    csr = generate_csr(cfg, key)
    write_csr(csr, cfg.csr_path)
    print(f"CSR written to {cfg.csr_path}")

if __name__ == '__main__':
    main()
