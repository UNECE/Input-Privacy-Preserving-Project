#Start BI Server 
kill $(lsof -i:5000 -t) 
python ../SERVER/psiServer.py 127.0.0.1 5000 ./DATASET_B_BANCA_ITALIA.csv ../PUBLIC_KEYS/BIkey&

sleep 5s # wait for psiServer to start webserver...
read -p "BI server started, press RETURN when both ISTAT and LINKER servers are online" yn

echo "Starting BI client..."
# create intersection file
python ../CLIENT/psiClient.py  127.0.0.1 5001 ./DATASET_B_BANCA_ITALIA.csv ../PUBLIC_KEYS/ISTATkey intersectionBI.txt

echo "Sending local BI file to linker..."
# encrypt intersection keys & sensitive data and send it to linker
python ../SEND_INTERSECTION/psiLinkerSendData.py 127.0.0.1 5002 3425245235 ./DATASET_B_BANCA_ITALIA.csv intersectionBI.txt P1
