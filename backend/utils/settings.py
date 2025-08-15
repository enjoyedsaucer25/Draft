from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    season: int = 2025
    roster_qb: int = 1
    roster_rb: int = 2
    roster_wr: int = 3
    roster_te: int = 0
    roster_flex: int = 1  # RB/WR/TE
    roster_k: int = 1
    roster_def: int = 1
    bench: int = 5

    class Config:
        env_prefix = "DA_"
        env_file = ".env"

settings = Settings()
