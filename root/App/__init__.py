"""
Services package for the Renewable Energy Forecasting API.

This package contains service modules that handle specific functionality:
- weather: Interacts with external weather APIs
- model: Manages ML model loading and prediction
- cache: Provides caching functionality
- auth: Handles API key validation and authentication
"""

__all__ = ["weather", "model", "cache", "auth"]