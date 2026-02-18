import subprocess, time, os, platform, sys

args = sys.argv

if len(args) == 2:
	port = int(args[1])
else:
	port = 8000

if os.path.exists('CONFIG') == False:
	with open('CONFIG', 'w') as f:
		f.write('first_run=True\n')

with open('CONFIG', 'r') as f:
	config = f.read().splitlines()
if config[0] == 'first_run=True':
	print("First run detected. Setting up the environment...\n")
	subprocess.run(['python3', './setup.py'])
	with open('CONFIG', 'w') as f:
		f.write('first_run=False\n')
try:
	if platform.system() == 'Windows':
		print("Starting application...\n")
		subprocess.run(['git', 'pull'])
		print("\nRunning migrations and starting server...\n")
		subprocess.run(['./.venv/Scripts/python.exe', 'manage.py', 'makemigrations'])

		subprocess.run(['./.venv/Scripts/python.exe', 'manage.py', 'migrate'])
		print(f"Starting server on http://127.0.0.1:{port}\n")
		subprocess.run(['./.venv/Scripts/python.exe', 'manage.py', 'runserver', f'0.0.0.0:{port}'])
	else:
		print("Starting application...\n")
		subprocess.run(['git', 'pull'])
		subprocess.run(['./.venv/bin/python3', 'manage.py', 'collectstatic', '--no-input'])
		print("\nRunning migrations and starting server...\n")
		subprocess.run(['./.venv/bin/python3', 'manage.py', 'makemigrations'])

		subprocess.run(['./.venv/bin/python3', 'manage.py', 'migrate'])
		print(f"Starting server on http://127.0.0.1:{port}\n")
		subprocess.run(['./.venv/bin/python3', 'manage.py', 'runserver', f'0.0.0.0:{port}'])
except KeyboardInterrupt:
	print('\n\nStopping server and exiting program')
	print('Server stopped, database saved')
