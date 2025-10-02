import subprocess, time
try:
	print("Starting application...\n")
	subprocess.run(['git', 'pull'])
	time.sleep(2)  # Wait for 2 seconds to ensure the environment is ready
	subprocess.run(['python3', './setup.py'])
	print("Running migrations and starting server...\n")
	subprocess.run(['./.venv/bin/python3', 'manage.py', 'makemigrations'])

	subprocess.run(['./.venv/bin/python3', 'manage.py', 'migrate'])

	subprocess.run(['./.venv/bin/python3', 'manage.py', 'runserver', '0.0.0.0:8000'])
except KeyboardInterrupt:
	print('\n\nexiting program')
