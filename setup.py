import subprocess

subprocess.run(['python3', '-m', 'vemv', '.venv'])

subprocess.run(['.venv/bin/pip', 'install', '-r', 'requirements.txt'])