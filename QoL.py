import subprocess, os, time, platform, sqlite3

i = input('QoL script name: >')
os = platform.system()
match i:
	case "cdb":
		subprocess.run(['rm', 'media/videos/*', 'media/templates/*'])
		conn = sqlite3.connect('db2.sqlite3')
		cursor = conn.cursor()
		cursor.execute('DELETE FROM app_video')
		cursor.execute('DELETE FROM app_comment')
		conn.commit()
		conn.close()
