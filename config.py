from dataclasses import dataclass


@dataclass
class Config:
    """Configuration class for bot settings."""
    bot_token: str
    admin_id: int
    group_id: str
