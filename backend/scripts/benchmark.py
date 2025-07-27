#!/usr/bin/env python
"""
Benchmark script for the authentication system.

This script benchmarks the performance of various authentication operations.

Usage:
    python -m scripts.benchmark [--iterations N] [--users N] [--verbose]
"""

import argparse
import asyncio
import random
import string
import time
from pathlib import Path
import sys

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.security import get_password_hash, verify_password
from app.core.security import create_access_token, create_refresh_token
from app.core.security import verify_token
from app.services.auth.totp import generate_totp_secret, verify_totp


async def benchmark_password_hashing(iterations=1000, verbose=False):
    """Benchmark password hashing performance."""
    print(f"Benchmarking password hashing ({iterations} iterations)...")
    
    # Generate random passwords
    passwords = [
        ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=12))
        for _ in range(iterations)
    ]
    
    # Benchmark hashing
    start_time = time.time()
    hashed_passwords = [get_password_hash(password) for password in passwords]
    hashing_time = time.time() - start_time
    
    # Benchmark verification
    start_time = time.time()
    for i in range(iterations):
        verify_password(passwords[i], hashed_passwords[i])
    verification_time = time.time() - start_time
    
    # Results
    print(f"Password hashing: {hashing_time:.2f}s total, {hashing_time/iterations*1000:.2f}ms per hash")
    print(f"Password verification: {verification_time:.2f}s total, {verification_time/iterations*1000:.2f}ms per verification")
    
    if verbose:
        print(f"Sample password: {passwords[0]}")
        print(f"Sample hash: {hashed_passwords[0]}")
    
    return hashing_time, verification_time


async def benchmark_token_operations(iterations=1000, verbose=False):
    """Benchmark JWT token operations."""
    print(f"\nBenchmarking JWT token operations ({iterations} iterations)...")
    
    # Generate random user data
    users = [
        {"sub": str(i), "username": f"user{i}", "role": "user"}
        for i in range(iterations)
    ]
    
    # Benchmark access token creation
    start_time = time.time()
    access_tokens = [create_access_token(data=user) for user in users]
    access_token_time = time.time() - start_time
    
    # Benchmark refresh token creation
    start_time = time.time()
    refresh_tokens = [create_refresh_token(data=user) for user in users]
    refresh_token_time = time.time() - start_time
    
    # Benchmark token verification
    start_time = time.time()
    for token in access_tokens:
        verify_token(token, "access")
    verification_time = time.time() - start_time
    
    # Results
    print(f"Access token creation: {access_token_time:.2f}s total, {access_token_time/iterations*1000:.2f}ms per token")
    print(f"Refresh token creation: {refresh_token_time:.2f}s total, {refresh_token_time/iterations*1000:.2f}ms per token")
    print(f"Token verification: {verification_time:.2f}s total, {verification_time/iterations*1000:.2f}ms per verification")
    
    if verbose:
        print(f"Sample user data: {users[0]}")
        print(f"Sample access token: {access_tokens[0]}")
    
    return access_token_time, refresh_token_time, verification_time


async def benchmark_totp_operations(iterations=100, verbose=False):
    """Benchmark TOTP operations."""
    print(f"\nBenchmarking TOTP operations ({iterations} iterations)...")
    
    # Generate TOTP secrets
    start_time = time.time()
    secrets = [generate_totp_secret() for _ in range(iterations)]
    secret_time = time.time() - start_time
    
    # Generate TOTP tokens
    start_time = time.time()
    tokens = []
    for secret in secrets:
        import pyotp
        totp = pyotp.TOTP(secret)
        tokens.append(totp.now())
    token_time = time.time() - start_time
    
    # Verify TOTP tokens
    start_time = time.time()
    for i in range(iterations):
        verify_totp(secrets[i], tokens[i])
    verification_time = time.time() - start_time
    
    # Results
    print(f"TOTP secret generation: {secret_time:.2f}s total, {secret_time/iterations*1000:.2f}ms per secret")
    print(f"TOTP token generation: {token_time:.2f}s total, {token_time/iterations*1000:.2f}ms per token")
    print(f"TOTP verification: {verification_time:.2f}s total, {verification_time/iterations*1000:.2f}ms per verification")
    
    if verbose:
        print(f"Sample TOTP secret: {secrets[0]}")
        print(f"Sample TOTP token: {tokens[0]}")
    
    return secret_time, token_time, verification_time


async def main():
    parser = argparse.ArgumentParser(description="Benchmark authentication operations")
    parser.add_argument(
        "--iterations", "-i", 
        type=int, 
        default=1000, 
        help="Number of iterations for each benchmark (default: 1000)"
    )
    parser.add_argument(
        "--totp-iterations", 
        type=int, 
        default=100, 
        help="Number of iterations for TOTP benchmarks (default: 100)"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Show verbose output"
    )
    
    args = parser.parse_args()
    
    print("Starting authentication system benchmark...\n")
    
    # Run benchmarks
    await benchmark_password_hashing(args.iterations, args.verbose)
    await benchmark_token_operations(args.iterations, args.verbose)
    await benchmark_totp_operations(args.totp_iterations, args.verbose)
    
    print("\nBenchmark complete!")


if __name__ == "__main__":
    asyncio.run(main())