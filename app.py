import os
import sys

# Entrypoint alias for Google Cloud Run / Buildpacks
from server import run_server, BASE_DIR

if __name__ == "__main__":
    os.chdir(BASE_DIR)
    run_server()
