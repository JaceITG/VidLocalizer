set /A count=0
:ping
ping 1.2.3.4 -n 1 -w 1000 > nul
set target=www.google.com
set /A count=count+1
ping %target% -n 1 | find "TTL="
if count geq 10 goto start
if errorlevel==1 goto ping

:start
(
start /min "VideoLocalizer" python3 .\\main.py
) | pause
exit