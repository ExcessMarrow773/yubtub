import os
import threading
from django.apps import AppConfig
import threading
from pathlib import Path
import importlib
import time
import threading
from pathlib import Path

class ChatConfig(AppConfig):
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'chat'

	def ready(self):
		# Only run watcher in the reloader child process
		if os.environ.get('RUN_MAIN') not in ('true', '1'):
			return

		BOT_FILE = Path(__file__).resolve().parent / "bot.py"

		# Import bot module lazily now that apps are ready
		try:
			bot_mod = {'mod': importlib.import_module(f"{__package__}.bot")}
		except Exception as exc:
			with open('debug.txt', 'a') as dbg:
				dbg.write(f'Failed importing chat.bot in ready(): {exc}\n')
			return

		def _watch_and_reload(interval=1.0):
			last_mtime = BOT_FILE.stat().st_mtime
			while True:
				try:
					mtime = BOT_FILE.stat().st_mtime
				except FileNotFoundError:
					mtime = None
				if mtime and mtime != last_mtime:
					last_mtime = mtime
					try:
						# reload and update reference in container
						bot_mod['mod'] = importlib.reload(bot_mod['mod'])
						with open("debug.txt", "a") as dbg:
							dbg.write(f"Reloaded chat.bot at {time.ctime(mtime)}\n")
						# optional: call a hook in bot.py to let it rebind handlers / swap state
						if hasattr(bot_mod['mod'], "on_reload"):
							try:
								bot_mod['mod'].on_reload()
							except Exception as e:
								with open("debug.txt", "a") as dbg:
									dbg.write(f"bot.on_reload() raised: {e}\n")
					except Exception as e:
						with open("debug.txt", "a") as dbg:
							dbg.write(f"Failed to reload chat.bot: {e}\n")
				time.sleep(interval)

		# start watcher that reloads module when bot.py changes
		threading.Thread(target=_watch_and_reload, daemon=True, name="chat-bot-watcher").start()