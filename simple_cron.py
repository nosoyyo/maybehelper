import os
import psutil

with open('pid', 'r') as pidfile:
    pid = pidfile.read()

p = psutil.Process(pid)

if not p.is_running():
    os.system('python3.6 bot.py')
