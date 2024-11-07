import environ

env = environ.Env()
environ.Env.read_env("Bloga/.env")

workers = env("WORKERS")
bind = "0.0.0.0:" + env("PORT")