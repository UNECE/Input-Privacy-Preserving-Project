"C:\Users\abel.dasylva\AppData\Local\Programs\Python\Python310\python.exe" ../SERVER/psiServer.py 127.0.0.1 5001 ./cbs_export_data.txt ../PUBLIC_KEYS/CBSkey&

REM CBS server started, press RETURN when both STATCAN and LINKER servers are online

::PAUSE

::REM Starting CBS client (create intersection file)...

::"C:\Users\abel.dasylva\AppData\Local\Programs\Python\Python310\python.exe" ../CLIENT/psiClient.py  127.0.0.1 5000 ./cbs_export_data.txt ../PUBLIC_KEYS/STATCANkey intersectionCBS.txt

::REM Sending local CBS file to linker (encrypt intersection keys and sensitive data and send it to linker)...

::"C:\Users\abel.dasylva\AppData\Local\Programs\Python\Python310\python.exe" ../SEND_INTERSECTION/psiLinkerSendData.py 127.0.0.1 5002 3425245235 ./cbs_export_data.txt intersectionCBS.txt P2