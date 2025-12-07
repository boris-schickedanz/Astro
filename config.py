"""
Configuration module for the Astro project.

This module loads environment variables and provides centralized configuration.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# GeoNames configuration
GEONAMES_USERNAME = os.getenv('GEONAMES_USERNAME')