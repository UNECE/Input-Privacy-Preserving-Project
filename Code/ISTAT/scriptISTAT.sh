#Start ISTAT Server 
kill $(lsof -i:5001 -t)
python ../SERVER/psiServer.py 127.0.0.1 5001 ./DATASET_A_ISTAT.csv ../PUBLIC_KEYS/ISTATkey&

sleep 5s # wait for psiServer to start webserver...
read -p "ISTAT server started, press RETURN when both BI and LINKER servers are online" yn

echo "Starting ISTAT client..."
# create intersection file
python ../CLIENT/psiClient.py  127.0.0.1 5000 ./DATASET_A_ISTAT.csv ../PUBLIC_KEYS/BIkey intersectionISTAT.txt

echo "Sending local BI file to linker..."
# encrypt intersection keys & sensitive data and send it to linker
python ../SEND_INTERSECTION/psiLinkerSendData.py 127.0.0.1 5002 3425245235 ./DATASET_A_ISTAT.csv intersectionISTAT.txt P2

