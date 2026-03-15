"""
E-Commerce Core Framework
Shared base classes for e-commerce platform automation
"""

from .browser import EcommerceBrowser
from .auth import AuthManager
from .cache import DataCache

__all__ = ['EcommerceBrowser', 'AuthManager', 'DataCache']
__version__ = '1.0.0'
