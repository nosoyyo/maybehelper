import os
import psutil


if 'pid' not in os.listdir():
    with open('pid', 'w'):
        pass
else:
    with open('pid', 'r') as pidfile:
        pid = int(pidfile.read())

p = psutil.Process(pid)

if not p.is_running():
    os.system('python3.6 bot.py')
