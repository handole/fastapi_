from functools import lru_cache
from pydantic import BaseSettings

class AppSettings(BaseSettings):
    app_name: str = "Base API Fastapi"
    admin_email: str = "base@mail.com"
    app_dir: str = "app.api:app"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_reload: bool = True
    api_prefix: str = "/api"
    docs_prefix: str = "/api"
    items_per_page: int = 12
    ignored_paths: str = "[login, register, openapi.json, docs]"
    fe_hostname: str = "https://staging-base.com"
    
    class Config:
        env_file: ".env"

    
class DBSettings(BaseSettings):
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = 'base'
    users_collection: str = "users"

    class Config:
        env_file = ".env"


class AuthSettings(BaseSettings):
    jwt_secret: str
    jwt_refresh_secret: str
    jwt_algoritm: str = "HS256"
    jwt_expiry_time: int # second

    class Config:
        env_file = ".env"


class LogSettings(BaseSettings):
    """One time setup for logging"""

    log_base_dirs: str
    log_backup_count: int
    log_date_format: str
    log_admin_file_name: str
    log_app_file_name: str
    log_audit_file_name: str
    log_error_file_name: str
    log_users_file_name: str
    log_task_file_name: str
    log_format: str
    log_interval: int
    log_level: str
    log_style: str
    log_when: str

    class Config:
        env_file = ".env"


# SETTING FUNCTIONS
# We are using the @lru_cache() decorator on top of each function
# the settings object will be created only once, the first time it's called.
@lru_cache()
def get_app_settings() -> AppSettings:
    return AppSettings()


@lru_cache()
def get_db_settings() -> DBSettings:
    return DBSettings()


@lru_cache
def get_auth_settings() -> AuthSettings:
    return AuthSettings()


# ADDITIONAL FUNCTIONS
def setup_log_settings():
    """One-time setup for logging"""

    import logging.config
    import os

    cfg = LogSettings()

    # Create logs folder if it doesn't exist.
    if not os.path.isdir(os.path.join(cfg.log_base_dirs)):
        os.makedirs(os.path.join(cfg.log_base_dirs))

    timed_rotating_file_handler_cfg = {
        "level": cfg.log_level,
        "class": "logging.handlers.TimedRotatingFileHandler",
        "when": cfg.log_when,
        "interval": cfg.log_interval,
        "backupCount": cfg.log_backup_count,
    }

    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": cfg.log_format,
                "style": cfg.log_style,
                "datefmt": cfg.log_date_format,
            }
        },
        "handlers": {
            "app_handler": {  # app log handler
                "filename": os.path.join(cfg.log_base_dirs, cfg.log_app_file_name),
                "formatter": "standard",
                **timed_rotating_file_handler_cfg,
            },
            "audit_handler": {  # audit log handler
                "filename": os.path.join(cfg.log_base_dirs, cfg.log_audit_file_name),
                **timed_rotating_file_handler_cfg,
            },
            "error_handler": {  # error log handler
                "filename": os.path.join(cfg.log_base_dirs, cfg.log_error_file_name),
                "formatter": "standard",
                **timed_rotating_file_handler_cfg,
            },
            
            "admin_handler": {  # consumers log handler
                "filename": os.path.join(cfg.log_base_dirs, cfg.log_admin_file_name),
                "formatter": "standard",
                **timed_rotating_file_handler_cfg,
            },
           
            "users_handler": {  # consumers log handler
                "filename": os.path.join(cfg.log_base_dirs, cfg.log_users_file_name),
                "formatter": "standard",
                **timed_rotating_file_handler_cfg,
            },
            
            "task_handler": {  # consumers log handler
                "filename": os.path.join(cfg.log_base_dirs, cfg.log_task_file_name),
                "formatter": "standard",
                **timed_rotating_file_handler_cfg,
            },
        },
        "loggers": {
            "": {
                "handlers": ["app_handler"],
                "level": cfg.log_level,
                "propagate": True,
            },
            "audit": {
                "handlers": ["audit_handler"],
                "level": cfg.log_level,
                "propagate": True,
            },
            "error": {
                "handlers": ["error_handler"],
                "level": cfg.log_level,
                "propagate": True,
            },
           
            "admin": {
                "handlers": ["admin_handler"],
                "level": cfg.log_level,
                "propagate": True,
            },
            
            "users": {
                "handlers": ["users_handler"],
                "level": cfg.log_level,
                "propagate": True,
            },
            
            "task": {
                "handlers": ["task_handler"],
                "level": cfg.log_level,
                "propagate": True,
            },
        },
    }

    logging.config.dictConfig(LOGGING_CONFIG)
