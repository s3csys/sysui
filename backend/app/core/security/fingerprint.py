from typing import Optional
import hashlib


def generate_fingerprint(user_agent: Optional[str]) -> Optional[str]:
    """
    Generate a fingerprint from a user agent string.
    
    Args:
        user_agent: The user agent string to generate a fingerprint from
        
    Returns:
        Optional[str]: The generated fingerprint, or None if no user agent provided
    """
    if not user_agent:
        return None
        
    # Create a fingerprint based on user agent
    # This helps prevent token reuse across different devices/browsers
    return hashlib.sha256(user_agent.encode()).hexdigest()[:32]


def verify_fingerprint(token_fingerprint: Optional[str], request_fingerprint: Optional[str], 
                      token_ip: Optional[str] = None, current_ip: Optional[str] = None) -> bool:
    """
    Verify that a token fingerprint matches a request fingerprint.
    Also optionally checks if the IP address has changed significantly.
    
    Args:
        token_fingerprint: The fingerprint stored in the token
        request_fingerprint: The fingerprint generated from the current request
        token_ip: The IP address stored in the token (optional)
        current_ip: The IP address from the current request (optional)
        
    Returns:
        bool: True if the fingerprints match (and IPs are consistent if provided), False otherwise
    """
    # If both fingerprints are None, skip verification
    if token_fingerprint is None and request_fingerprint is None:
        return True
    
    # If one fingerprint is None but the other isn't, verification fails
    if token_fingerprint is None or request_fingerprint is None:
        return False
    
    # Compare fingerprints
    fingerprint_match = token_fingerprint == request_fingerprint
    
    # If fingerprints don't match, no need to check IPs
    if not fingerprint_match:
        return False
    
    # If IP addresses are provided, check if they're consistent
    if token_ip and current_ip:
        # For IPv4 addresses, compare the first three octets
        # This allows for some mobility within the same network
        if '.' in token_ip and '.' in current_ip:  # IPv4
            token_network = '.'.join(token_ip.split('.')[:3])
            current_network = '.'.join(current_ip.split('.')[:3])
            return token_network == current_network
        # For IPv6 addresses, compare the first 4 segments
        elif ':' in token_ip and ':' in current_ip:  # IPv6
            token_network = ':'.join(token_ip.split(':')[:4])
            current_network = ':'.join(current_ip.split(':')[:4])
            return token_network == current_network
    
    # If no IP check or IP formats don't match, rely on fingerprint match
    return fingerprint_match