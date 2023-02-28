kill $(lsof -i:5002 -t)
python psiLinker.py 127.0.0.1 5002
