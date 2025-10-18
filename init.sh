# Get the name of the repo export 
MY_REPO=$(ls -d "/home/onyxia/work"/*/ | head -n 1 | xargs basename) 

# Install GDAL
curl -sL "https://url.geocarpentry.org/gdal-ubuntu" | bash

# Install dependencies
cd $MY_REPO
uv sync

# Set VSCode's default interpreter path
cd ..
mkdir -p .vscode

echo '{"python.defaultInterpreterPath":"./'$MY_REPO'/.venv/bin/python"}' >> .vscode/settings.json
