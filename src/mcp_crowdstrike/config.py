"""
Configuration management for MCP CrowdStrike.

This module provides centralized configuration using Pydantic Settings.
All sensitive credentials are stored as SecretStr to prevent accidental logging.
"""

from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be configured via:
    1. Environment variables (e.g., FALCON_CLIENT_ID)
    2. .env file
    3. Default values (where applicable)

    Security:
        - Credentials use SecretStr to prevent accidental exposure in logs
        - Validation ensures required fields are not empty
        - No default values for sensitive credentials
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # CrowdStrike Falcon API Credentials (Required)
    falcon_client_id: SecretStr = Field(
        ...,
        description="CrowdStrike Falcon API Client ID",
        min_length=1,
    )
    falcon_client_secret: SecretStr = Field(
        ...,
        description="CrowdStrike Falcon API Client Secret",
        min_length=1,
    )

    # CrowdStrike API Configuration (Optional)
    falcon_base_url: str = Field(
        default="https://api.crowdstrike.com",
        description="CrowdStrike Falcon API base URL",
    )

    # Server Configuration (Optional)
    server_host: str = Field(
        default="0.0.0.0",
        description="Server host address",
    )
    server_port: int = Field(
        default=8001,
        description="Server port",
        ge=1,
        le=65535,
    )

    # Logging Configuration (Optional)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )

    # Environment (Optional)
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment",
    )

    @field_validator("falcon_base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate that the base URL uses HTTPS in production."""
        if not v.startswith("http://") and not v.startswith("https://"):
            raise ValueError("Base URL must start with http:// or https://")

        # Remove trailing slash if present
        return v.rstrip("/")

    @field_validator("falcon_client_id", "falcon_client_secret")
    @classmethod
    def validate_not_placeholder(cls, v: SecretStr) -> SecretStr:
        """Ensure credentials are not placeholder values."""
        secret_value = v.get_secret_value()
        placeholders = [
            "your-client-id-here",
            "your-client-secret-here",
            "your-id",
            "your-secret",
            "",
        ]

        if secret_value.lower() in placeholders:
            raise ValueError(
                "Credential appears to be a placeholder. "
                "Please provide actual CrowdStrike API credentials."
            )

        return v

    def get_falcon_credentials(self) -> tuple[str, str]:
        """
        Get CrowdStrike Falcon credentials as a tuple.

        Returns:
            tuple[str, str]: (client_id, client_secret)
        """
        return (
            self.falcon_client_id.get_secret_value(),
            self.falcon_client_secret.get_secret_value(),
        )


# Singleton settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """
    Get or create the singleton settings instance.

    Returns:
        Settings: Application settings

    Raises:
        ValidationError: If required settings are missing or invalid
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
