#!/usr/bin/env python3
"""
Minimal type-safe CLI tool for encrypting and decrypting HTML files.

Usage:
    python encrypt.py encrypt input.html --password PASSWORD
    python encrypt.py decrypt input-encrypted.html --password PASSWORD

This script validates passwords, encrypts HTML files, and decrypts them.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
SALT_SIZE = 16
KEY_SIZE = 32
IV_SIZE = 16
PASSWORD_MIN_LENGTH = 8


def validate_password(password: str) -> None:
    """Validate the password against minimum requirements."""
    if len(password) < PASSWORD_MIN_LENGTH:
        logger.error("Password validation failed: Too short.")
        raise ValueError("Password must be at least 8 characters long.")
    if not any(char.islower() for char in password):
        logger.error("Password validation failed: Missing lowercase letter.")
        raise ValueError("Password must contain at least one lowercase letter.")
    if not any(char.isupper() for char in password):
        logger.error("Password validation failed: Missing uppercase letter.")
        raise ValueError("Password must contain at least one uppercase letter.")
    if not any(char.isdigit() for char in password):
        logger.error("Password validation failed: Missing digit.")
        raise ValueError("Password must contain at least one digit.")
    if not any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/" for char in password):
        logger.error("Password validation failed: Missing special character.")
        raise ValueError("Password must contain at least one special character.")


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a cryptographic key from the password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=100_000,
        backend=default_backend(),
    )
    return kdf.derive(password.encode())


def encrypt_file(input_path: Path, password: str, allow_unsafe: bool = False) -> None:
    """Encrypt an HTML file with the given password.

    Args:
        input_path: Path to the HTML file to encrypt.
        password: User-supplied password.
        allow_unsafe: If True, skip security validation of the password. This
            is intended for users who knowingly accept the risks of a weak
            password (e.g. for a quick test). The default is False.
    """
    try:
        # Password validation can be heavy-handed for some workflows; provide a
        # flag to bypass it when the caller explicitly requests it.
        if not allow_unsafe:
            validate_password(password)

        # Read the input file
        plaintext = input_path.read_text(encoding="utf-8").encode("utf-8")

        # Generate salt and derive key
        salt = os.urandom(SALT_SIZE)
        key = derive_key(password, salt)

        # Generate random IV
        iv = os.urandom(IV_SIZE)

        # Encrypt the plaintext
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        padder = PKCS7(algorithms.AES.block_size).padder()
        padded_plaintext = padder.update(plaintext) + padder.finalize()
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

        # Write the encrypted file
        output_path = input_path.with_name(f"{input_path.stem}-encrypted.html")
        with output_path.open("wb") as f:
            f.write(salt + iv + ciphertext)

        print(f"Encrypted file written to: {output_path}")
        logger.info(f"Encryption successful: {output_path}")
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        raise


def decrypt_file(input_path: Path, password: str) -> None:
    """Decrypt an encrypted HTML file with the given password."""
    try:
        # Read the encrypted file
        data = input_path.read_bytes()

        # Extract salt, IV, and ciphertext
        salt = data[:SALT_SIZE]
        iv = data[SALT_SIZE : SALT_SIZE + IV_SIZE]
        ciphertext = data[SALT_SIZE + IV_SIZE :]

        # Derive key
        key = derive_key(password, salt)

        # Decrypt the ciphertext
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        # Remove padding
        unpadder = PKCS7(algorithms.AES.block_size).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

        # Write the decrypted file
        output_path = input_path.with_name(f"{input_path.stem}-decrypted.html")
        output_path.write_text(plaintext.decode("utf-8"), encoding="utf-8")

        print(f"Decrypted file written to: {output_path}")
        logger.info(f"Decryption successful: {output_path}")
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise


def main() -> None:
    """Entry point for the CLI tool."""
    try:
        parser = argparse.ArgumentParser(description="Encrypt or decrypt HTML files.")
        subparsers = parser.add_subparsers(dest="command", required=True)

        # Encrypt command
        encrypt_parser = subparsers.add_parser("encrypt", help="Encrypt an HTML file.")
        encrypt_parser.add_argument(
            "input", type=Path, help="Path to the input HTML file."
        )
        encrypt_parser.add_argument(
            "--password", required=True, help="Password for encryption."
        )
        encrypt_parser.add_argument(
            "--allow-unsafe-password",
            action="store_true",
            help="Skip password strength validation (unsafe).",
        )

        # Decrypt command
        decrypt_parser = subparsers.add_parser(
            "decrypt", help="Decrypt an encrypted HTML file."
        )
        decrypt_parser.add_argument(
            "input", type=Path, help="Path to the encrypted HTML file."
        )
        decrypt_parser.add_argument(
            "--password", required=True, help="Password for decryption."
        )

        args = parser.parse_args()

        if args.command == "encrypt":
            encrypt_file(args.input, args.password, allow_unsafe=getattr(args, "allow_unsafe_password", False))
        elif args.command == "decrypt":
            decrypt_file(args.input, args.password)
    except Exception as e:
        logger.critical(f"An error occurred: {e}")
        raise


if __name__ == "__main__":
    main()
