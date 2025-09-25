import subprocess, time
print("Starting application...\n")
time.sleep(2)  # Wait for 2 seconds to ensure the environment is ready
subprocess.run(['./.venv/bin/python3', './setup.py'])
print("Running migrations and starting server...\n")
subprocess.run(['./.venv/bin/python3', 'manage.py', 'makemigrations'])

subprocess.run(['./.venv/bin/python3', 'manage.py', 'collectstatic', '--noinput'])

subprocess.run(['./.venv/bin/python3', 'manage.py', 'migrate'])

subprocess.run(['./.venv/bin/python3', 'manage.py', 'runserver'])