import subprocess
print("Setting up virtual environment...\n")
subprocess.run(['python3', '-m', 'venv', '.venv'])
print("Installing required packages...\n")
subprocess.run(['.venv/bin/pip', 'install', '-r', 'requirements.txt'])
subprocess.run(['.venv/bin/python', 'manage.py', 'createsuperuser', '--noinput', '--username', 'admin', '--email', '', '--skip-checks'])

print("\n\nSetup complete. To activate the virtual environment, run 'source .venv/bin/activate'.")


