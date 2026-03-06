"""
JEP Python SDK - Complete SDK for HJS Protocol

Implements all 4 core primitives defined in IETF draft-wang-hjs-judgment-event-00:

- **Judgment**: Record structured decisions (who, what, when, context)
- **Delegation**: Transfer authority with scope and expiry
- **Termination**: End responsibility chains
- **Verification**: Validate record integrity and chains

Example:
    >>> from jep import HJSClient
    >>> 
    >>> # Initialize client
    >>> client = JEPClient(api_key="your_key")
    >>> 
    >>> # Record a judgment
    >>> judgment = client.judgment(
    ...     entity="user@example.com",
    ...     action="approve",
    ...     scope={"amount": 100}
    ... )
    >>> print(f"Recorded: {judgment['id']}")
    >>> 
    >>> # Verify the record
    >>> verification = client.verify(judgment['id'])
    >>> print(f"Valid: {verification['status']}")
"""

from .client import HJSClient

__version__ = "0.1.0"
__all__ = [
    'JEPClient',
]

# For backward compatibility, create_judgment is available via client.judgment
