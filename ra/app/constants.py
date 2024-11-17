import os

RESOURCE_DIR = os.path.join("app", "static", "res")


# Create the folders if they don't exist
if not os.path.isdir(RESOURCE_DIR):
    os.mkdir(RESOURCE_DIR)