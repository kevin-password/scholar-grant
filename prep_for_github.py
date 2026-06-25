import os
import subprocess

# 1. Create .gitignore so we don't upload junk
gitignore_content = """
venv/
__pycache__/
*.pyc
db.sqlite3
*.log
.DS_Store
fix_*.py
"""
with open('.gitignore', 'w') as f:
    f.write(gitignore_content)

# 2. Install Gunicorn (the server that runs Django in production)
print("Installing Gunicorn...")
subprocess.run(['pip', 'install', 'gunicorn'])

# 3. Create requirements.txt (a list of all packages your app needs)
print("Generating requirements.txt...")
subprocess.run(['pip', 'freeze', '>', 'requirements.txt'], shell=True)

# 4. Update settings.py for the live internet
settings_path = 'scholar_grants/settings.py'
with open(settings_path, 'r') as f:
    content = f.read()

# Change DEBUG to False (required for live hosting)
content = content.replace('DEBUG = True', 'DEBUG = False')
# Allow Render.com to host the app
content = content.replace("ALLOWED_HOSTS = []", "ALLOWED_HOSTS = ['*']")

with open(settings_path, 'w') as f:
    f.write(content)

print("✅ Project is prepped and ready for GitHub!")