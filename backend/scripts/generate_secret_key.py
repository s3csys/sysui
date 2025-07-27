#!/usr/bin/env python
"""
Secret key generator script.

Generates a secure random secret key for use in the application.

Usage:
    python -m scripts.generate_secret_key
"""

import secrets
import string
import argparse


def generate_secret_key(length=64):
    """Generate a secure random secret key.
    
    Args:
        length: Length of the secret key (default: 64)
        
    Returns:
        A secure random string
    """
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def main():
    parser = argparse.ArgumentParser(description="Generate a secure random secret key")
    parser.add_argument(
        "-l", "--length", 
        type=int, 
        default=64, 
        help="Length of the secret key (default: 64)"
    )
    args = parser.parse_args()
    
    secret_key = generate_secret_key(args.length)
    print("\nGenerated Secret Key:")
    print("=======================")
    print(secret_key)
    print("\nAdd this to your .env file as:")
    print(f"SECRET_KEY='{secret_key}'")
    print("\nKeep this key secure and don't share it!")


if __name__ == "__main__":
    main()