import subprocess
print("Setting up virtual environment...")
subprocess.run(['python3', '-m', 'venv', '.venv'])
print("Installing required packages...")
subprocess.run(['.venv/bin/pip', 'install', '-r', 'requirements.txt'])

print("Setup complete. To activate the virtual environment, run 'source .venv/bin/activate'.")