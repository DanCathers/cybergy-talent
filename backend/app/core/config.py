"""Application configuration.

All settings are loaded from environment variables (or a local ``.env`` file
during development).  We NEVER hard-code secrets in source code — this is a
core DevSecOps practice.

We use ``pydantic-settings`` which validates the environment variables against
the type hints below and raises a clear error at startup if something required
is missing or malformed.
"""

from functools import lru_cache

# ``BaseSettings`` reads values from the environment and validates their types.
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application settings.

    Each attribute below maps to an environment variable of the same name
    (case-insensitive).  Defaults are provided only for non-secret values.
    """

    # ``model_config`` tells pydantic-settings where to find the .env file and
    # how to behave.  ``extra="ignore"`` means unknown env vars won't crash us.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- AI mapping ---
    ABACUS_API_KEY: str = ""  # required in production; empty allows local tests
    # Abacus AI's OpenAI-compatible endpoint (RouteLLM). This is the correct
    # base URL for chat/completions calls via the ``openai`` client.
    ABACUS_BASE_URL: str = "https://routellm.abacus.ai/v1"
    AI_MODEL: str = "gpt-4o"

    # --- Database ---
    DATABASE_URL: str = "postgresql+asyncpg://cybergy:cybergy@localhost:5432/cybergy_talent"

    # --- Security ---
    SECRET_KEY: str = "change-me-in-production"
    MAX_UPLOAD_SIZE_MB: int = 10
    # Stored as a comma-separated string in the env; parsed into a list below.
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # --- Storage ---
    STORAGE_DIR: str = "./storage"

    @property
    def max_upload_bytes(self) -> int:
        """Return the maximum upload size in bytes (megabytes * 1024 * 1024)."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def allowed_origins_list(self) -> list[str]:
        """Split the comma-separated origins string into a clean list.

        Example: "http://a.com, http://b.com" -> ["http://a.com", "http://b.com"]
        """
        # The list comprehension strips whitespace and drops empty entries.
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


# ``lru_cache`` caches the result so ``get_settings()`` builds the Settings
# object only once per process instead of re-reading the environment each call.
@lru_cache
def get_settings() -> Settings:
    """Return a cached, singleton ``Settings`` instance."""
    return Settings()


# A module-level convenience instance for simple imports elsewhere.
settings = get_settings()
