from . import config

app_settings = config.get_app_settings()
auth_settings = config.get_auth_settings()
db_settings = config.get_db_settings()


# init log setup
config.setup_log_settings()