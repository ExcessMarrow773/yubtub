import subprocess, time, os, platform

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
		time.sleep(2)  # Wait for 2 seconds to ensure the environment is ready
		print("\nRunning migrations and starting server...\n")
		subprocess.run(['./.venv/Scripts/python.exe', 'manage.py', 'makemigrations'])

		subprocess.run(['./.venv/Scripts/python.exe', 'manage.py', 'migrate'])
		print("Starting server on http://127.0.0.1:8000\n")
		subprocess.run(['./.venv/Scripts/python.exe', 'manage.py', 'runserver', '0.0.0.0:80'])
	else:
		print("Starting application...\n")
		subprocess.run(['git', 'pull'])
		time.sleep(2)  # Wait for 2 seconds to ensure the environment is ready
		print("\nRunning migrations and starting server...\n")
		subprocess.run(['./.venv/bin/python3', 'manage.py', 'makemigrations'])

		subprocess.run(['./.venv/bin/python3', 'manage.py', 'migrate'])
		print("Starting server on http://127.0.0.1:8000\n")
		subprocess.run(['./.venv/bin/python3', 'manage.py', 'runserver', '0.0.0.0:8000'])
except KeyboardInterrupt:
	print('\n\nStopping server and exiting program')
	time.sleep(2.2)
	print('Server stopped, database saved')
