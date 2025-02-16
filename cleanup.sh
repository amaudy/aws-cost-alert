#!/bin/bash

# Remove deployment artifacts
rm -rf package/
rm -f deployment.zip

# Remove any log files
rm -f *.log

# Remove any local environment files
rm -f .env*

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*.pyd" -delete
