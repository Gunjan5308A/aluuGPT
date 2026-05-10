"""
Configuration Management for AI Platform
Handles environment variables, API keys, and model configuration
"""

import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # API Configuration
    models: List[str] = []
    api_keys: List[str] = []
    base_urls: List[str] = []
    
    # Single model configuration
    primary_model: Optional[str] = None
    primary_api_key: Optional[str] = None
    primary_base_url: Optional[str] = None
    
    # Animation settings
    animation_width: int = 1280
    animation_height: int = 720
    animation_fps: int = 30
    animation_quality: str = "high"
    
    # Chat history
    enable_chat_history: bool = True
    embedding_model: str = "text-embedding-3-small"
    database_path: str = "/tmp/chat_history.db" if os.environ.get("VERCEL") == "1" else "./data/chat_history.db"
    max_context_tokens: int = 2000

    
    # UI settings
    default_theme: str = "dark"
    ui_port: int = 8000
    debug_mode: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **data):
        super().__init__(**data)
        # Parse comma-separated values
        if isinstance(self.models, str):
            self.models = [m.strip() for m in self.models.split(",") if m.strip()]
        if isinstance(self.api_keys, str):
            self.api_keys = [k.strip() for k in self.api_keys.split(",") if k.strip()]
        if isinstance(self.base_urls, str):
            self.base_urls = [u.strip() for u in self.base_urls.split(",") if u.strip()]


def get_settings() -> Settings:
    """Get application settings"""
    return Settings()


class ModelConfig:
    """Manage model configuration and selection"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.models = self._parse_models()

    def _parse_models(self) -> Dict[str, Dict[str, str]]:
        """Parse and return available models"""
        models = {}

        # Use primary model if configured
        if self.settings.primary_model:
            models["primary"] = {
                "name": self.settings.primary_model,
                "api_key": self.settings.primary_api_key,
                "base_url": self.settings.primary_base_url,
            }
            return models

        # Parse multiple models
        for i, model_name in enumerate(self.settings.models):
            api_key = (
                self.settings.api_keys[i]
                if i < len(self.settings.api_keys)
                else None
            )
            base_url = (
                self.settings.base_urls[i]
                if i < len(self.settings.base_urls)
                else "https://api.openai.com/v1"
            )

            models[f"model_{i}"] = {
                "name": model_name,
                "api_key": api_key,
                "base_url": base_url,
            }

        return models

    def get_model_for_task(self, task_type: str) -> Dict[str, str]:
        """
        Get appropriate model for task type
        - think: Use larger/more capable model
        - fast: Use smaller/faster model
        - animation: Use model designed for structured output
        """
        if len(self.models) == 1 or self.settings.primary_model:
            return list(self.models.values())[0]

        # Round-robin or task-specific selection
        model_list = list(self.models.values())

        if task_type == "think":
            # Use first (typically most capable)
            return model_list[0]
        elif task_type == "fast":
            # Use fastest available (prefer smaller models)
            return model_list[-1] if len(model_list) > 1 else model_list[0]
        elif task_type == "animation":
            # Use dedicated model if available, else first
            return model_list[1] if len(model_list) > 1 else model_list[0]
        else:
            return model_list[0]

    def get_all_models(self) -> Dict[str, Dict[str, str]]:
        """Get all configured models"""
        return self.models


# Initialize global settings
settings = get_settings()
model_config = ModelConfig(settings)
