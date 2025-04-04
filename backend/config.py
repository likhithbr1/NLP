# Database settings
DB_USER = "root"
DB_PASSWORD = "admin"
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "chatbot"

DB_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Model config
MODEL_PATH = "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"  # Path to your local GGUF file
N_CTX = 2048
N_THREADS = 6
VERBOSE = True
