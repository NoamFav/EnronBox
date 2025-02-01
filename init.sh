#!/bin/bash

# Create scripts directory and files
mkdir -p scripts

# Create script files
touch scripts/setup.cmd
cat <<EOL >scripts/setup.sh
#!/bin/bash
# Setup environment script
echo "Setting up the environment..."
EOL

chmod +x scripts/setup.sh
touch scripts/tmux_config.sh

# Create src directory structure
mkdir -p src/core/model
mkdir -p src/core/nlu
mkdir -p src/integrations/eclipse
mkdir -p src/integrations/intelliJ
mkdir -p src/integrations/neovim
mkdir -p src/integrations/vscode
mkdir -p src/memory/db
mkdir -p src/memory/embeddings
mkdir -p src/stt/engine
mkdir -p src/stt/preprocessing
mkdir -p src/tts/voice_profiles
mkdir -p src/utils
mkdir -p tests

# Create core files
touch src/core/model/Llama.py
touch src/core/nlu/context_manager.py
cat <<EOL >src/core/nlu/intent_parser.py
# Intent parser module
EOL

# Create integration files
touch src/integrations/eclipse/extension.c
touch src/integrations/intelliJ/extension.java
touch src/integrations/neovim/ai.lua
touch src/integrations/neovim/lsp.lua
touch src/integrations/vscode/extension.ts

# Create memory files
touch src/memory/db/core.py
cat <<EOL >src/memory/db/schema.py
# Database schema definitions
EOL

touch src/memory/embeddings/chroma.py
touch src/memory/embeddings/raw.sql

# Create STT files
touch src/stt/engine/ai.rs
cat <<EOL >src/stt/engine/engine.rs
// STT Engine core
EOL

touch src/stt/engine/functions.rs
cat <<EOL >src/stt/engine/raw.rs
// Raw audio processing
EOL

touch src/stt/engine/utils.rs
touch src/stt/preprocessing/audio_utils.rs

# Create TTS files
touch src/tts/synthesizer.py
touch src/tts/voice_profiles/default_profile.json
touch src/tts/voice_profiles/default_profile.toml
touch src/tts/voice_profiles/default_profile.xml
touch src/tts/voice_profiles/default_profile.yml

# Create utils files
touch src/utils/config_loader.py
touch src/utils/logger.rs

# Create test files
touch tests/memory_tests.rs
touch tests/stt_test.py

# Additional configuration files
cat <<EOL >setup.py
from setuptools import setup, find_packages

setup(
    name='ai-coding-assistant',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'ai-assistant=src.core.nlu.intent_parser:main',
        ],
    },
)
EOL

cat <<EOL >pyproject.toml
[tool.poetry]
name = "ai-coding-assistant"
version = "0.1.0"
description = "Voice-driven AI coding assistant"
authors = ["Your Name <your.email@example.com>"]

[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"
EOL

# Final output
echo "Project structure has been created successfully."
