#!/usr/bin/env python
"""
SSL Certificate Generator Script.

Generates a self-signed SSL certificate for development purposes.

Usage:
    python -m scripts.generate_cert [--days 365] [--output-dir ./certs]
"""

import argparse
import datetime
import os
from pathlib import Path


def generate_self_signed_cert(output_dir="./certs", days=365):
    """Generate a self-signed SSL certificate.
    
    Args:
        output_dir: Directory to save the certificate files
        days: Validity period in days
        
    Returns:
        Tuple of (cert_path, key_path)
    """
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
    except ImportError:
        print("Error: Required packages not installed.")
        print("Please install with: pip install cryptography")
        return None, None
    
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate key
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Generate certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "SysUI Development"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=days)
    ).add_extension(
        x509.SubjectAlternativeName([x509.DNSName("localhost")]),
        critical=False,
    ).sign(key, hashes.SHA256())
    
    # Write certificate and key to files
    cert_path = output_path / "cert.pem"
    key_path = output_path / "key.pem"
    
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    with open(key_path, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    return cert_path, key_path


def main():
    parser = argparse.ArgumentParser(description="Generate a self-signed SSL certificate")
    parser.add_argument(
        "--days", 
        type=int, 
        default=365, 
        help="Validity period in days (default: 365)"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="./certs", 
        help="Directory to save the certificate files (default: ./certs)"
    )
    
    args = parser.parse_args()
    
    print(f"Generating self-signed SSL certificate valid for {args.days} days...")
    cert_path, key_path = generate_self_signed_cert(args.output_dir, args.days)
    
    if cert_path and key_path:
        print(f"\nCertificate generated successfully!")
        print(f"Certificate: {cert_path}")
        print(f"Private key: {key_path}")
        print("\nTo use with Uvicorn, run:")
        print(f"uvicorn app.main:app --ssl-keyfile={key_path} --ssl-certfile={cert_path}")
        print("\nOr add these to your .env file:")
        print(f"SSL_KEYFILE={key_path}")
        print(f"SSL_CERTFILE={cert_path}")
    else:
        print("\nFailed to generate certificate.")


if __name__ == "__main__":
    main()