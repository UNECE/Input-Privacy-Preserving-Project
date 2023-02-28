"C:\Users\abel.dasylva\AppData\Local\Programs\Python\Python310\python.exe" ../SERVER/psiServer.py 127.0.0.1 5000 ./statcan_import_data.txt ../PUBLIC_KEYS/STATCANkey&

REM STATCAN server started, press RETURN when both CBS and LINKER servers are online

::PAUSE

REM Starting STATCAN client (create intersection file)...
 
"C:\Users\abel.dasylva\AppData\Local\Programs\Python\Python310\python.exe" ../CLIENT/psiClient.py  127.0.0.1 5001 ./statcan_import_data.txt ../PUBLIC_KEYS/CBSkey intersectionSTATCAN.txt

::REM Sending local STATCAN file to linker (encrypt intersection keys and  sensitive data and send it to linker)...

::"C:\Users\abel.dasylva\AppData\Local\Programs\Python\Python310\python.exe" ../SEND_INTERSECTION/psiLinkerSendData.py 127.0.0.1 5002 3425245235 ./statcan_import_data.txt intersectionSTATCAN.txt P1