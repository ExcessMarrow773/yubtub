import subprocess, os, time, platform, sqlite3

i = input('QoL script name: >')
os = platform.system()
match i:
	case "cdb":
		subprocess.run(['rm media/videos/* media/thumbnail/*'], shell=True)
		conn = sqlite3.connect('db.sqlite3')
		cursor = conn.cursor()
		cursor.execute('DELETE FROM app_video')
		cursor.execute('DELETE FROM app_videocomment')
		cursor.execute('DELETE FROM app_postcomment')
		cursor.execute('DELETE FROM app_video_likedUsers')
		cursor.execute('DELETE FROM app_video_viewedUsers')
		cursor.execute('DELETE FROM app_post')
		cursor.execute('DELETE FROM polls_question')
		cursor.execute('DELETE FROM polls_choice')
		conn.commit()
		conn.close()
	case _:
		subprocess.run(['./.venv/bin/python', './manage.py', 'collectstatic', '--no-input'])