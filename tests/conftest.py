"""
Pytest configuration for Asset Management tests.
"""

import pytest
import sys
from pathlib import Path

# Add project root containing 'app' to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture(scope="session")
def anyio_backend():
    """Configure pytest-asyncio."""
    return "asyncio"
