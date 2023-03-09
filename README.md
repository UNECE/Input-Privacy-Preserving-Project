# Private Set Intersection with Analytics

This application provides a solution to intersect data provided by two parties on a common shared identifier in a privacy preserving way and to perform statistics on the data obtained by the intersection.

The code in this repository is based on the [work](https://github.com/istat-methodology/PrivateSetIntersectionWithAnalytics) by Fabrizio de Fausti from IStat. It is a port of the original work from Python 2 to Python 3 with some minor changes to make the code generically usable for comparable scenario's with arbitrary parties.

To perform private set intersection you need 2 parties, and one of them needs to run a PSI Server. The other party runs a PSI Client which exchanges data with the PSI Server and obtains the intersection. Both parties should switch roles so both obtain the same intersection. After intersection it is possible to perform queries in a privacy preserving manner with help of a neutral helper party.

- Both data holder parties only learn the intersection and the size of the other parties population.
- The data holder parties do not learn sensitive input data.
- A data holder party performing a query also learns the aggregated outcome.
- The linker only learns the size of the intersection and size of the sensitive dataset.

The code is structured as follows:
- SERVER: contains the PSI Server code (user: data holder parties)
- CLIENT: contains the PSI Client code (user: data holder parties)
- LINKER: contains the Linker code to perform private analytics (user: linker party)
- SEND_INTERSECTION: contains code to send data to the linker (user: data holder parties)
- SEND_QUERY: contains code to send and receive a query to the linker (user: data holder parties)
- AES: contains shared code to help with AES encryption
- ISTAT: contains synthetic sample data and usage scripts for the example usage (data holder party 1)
- BI: contains synthetic sample data and usage scripts for the example usage (data holder party 2)

# Example Usage
Suppose we have 2 parties: **ISTAT (party 1)** and **BANCA ITALIA (BI, party 2)** and a simulation of the protocol on a single machine. Both parties run a PSI server and a PSI client to perform the private intersection.

## Intersection

### To run a PSI server:
`cd Code`  
`python ./SERVER/psiServer.py ip_adress tcp_port_nr input_datafile output_public_key_file`  
example for party 1: `python ./SERVER/psiServer.py 127.0.0.1 5001 ./ISTAT/DATASET_A_ISTAT.csv ./PUBLIC_KEYS/ISTATkey`

### To perform intersection with the other party:
`cd Code`  
`python ./CLIENT/psiClient.py  ip_adress tcp_port_nr input_datafile other_party_public_key_file output_intersection_file`  
example for party 2: `python ./CLIENT/psiClient.py  127.0.0.1 5001 ./BI/DATASET_B_BANCA_ITALIA.csv ./PUBLIC_KEYS/ISTATkey ./BI/intersectionBI.txt`

### Reverse roles
Party 2 now has the intersection. Both parties should reverse roles and perform the same steps to create the (identical) intersection file for party 1  
example for party 2: `python ./SERVER/psiServer.py 127.0.0.1 5000 ./BI/DATASET_B_BANCA_ITALIA.csv ./PUBLIC_KEYS/BIkey`  
example for party 1: `python ./CLIENT/psiClient.py  127.0.0.1 5000 ./ISTAT/DATASET_A_ISTAT.csv ./PUBLIC_KEYS/BIkey ./ISTAT/intersectionISTAT.txt`

### Key management
The sharing of the **public** RSA keys for encryption is not part of the protocol. They are are directy read from a shared output folder. In a real-world scenario the keys have to be exchanged between data holder parties after the respective servers have started and key-pairs are generated by the servers.

### Kill PSI Server:
`ctrl-c`  
`kill $(lsof -i:port-nr -t)` e.g. `kill $(lsof -i:5000 -t)`

## Analysis
To perform privacy preserving analysis you need another neutral helper party. The helper party runs a Linker Server. Both party 1 and party 2 send their encrypted intersection keys and encrypted sensitive data to the Linker. When both datasets are registered at the linker, the parties can send queries to the linker and receive aggregate results.

### To run a Linker server:
`cd Code`  
`python ./LINKER/psiLinker.py ip_adress tcp_port_nr`  
example: `python ./psiLinker.py 127.0.0.1 5002`

### To send data to the Linker:
When the linker is up and running, BOTH parties should send their (identical) intersected keys and their sensitive data to the linker (both encrypted):  
`cd Code`  
`python ./SEND_INTERSECTION/psiLinkerSendData.py linker_ip_adress linker_tcp_port_nr shared_encryption_key input_datafile intersection_file party-id`  
example for party 1: `python ./SEND_INTERSECTION/psiLinkerSendData.py 127.0.0.1 5002 3425245235 ./ISTAT/DATASET_A_ISTAT.csv ./ISTAT/intersectionISTAT.txt P1`  
example for party 2: `python ./SEND_INTERSECTION/psiLinkerSendData.py 127.0.0.1 5002 3425245235 ./BI/DATASET_B_BANCA_ITALIA.csv ./BI/intersectionBI.txt P2`

### To perform queries / analysis:
When the linker received all datasets it is possible for a party to perform a query 
`cd Code`   
`python ./SEND_QUERY/psiLinkerSendQuery.py linker_ip_adress linker_tcp_port_nr query-columns party-id shared_encryption_key`  
example: `python ./SEND_QUERY/psiLinkerSendQuery.py 127.0.0.1 5002 "CLASSE_ETA, CLASSE_REDDITO" P2 3425245235`

### Kill Linker:
`ctrl-c`  
`kill $(lsof -i:port-nr -t)` e.g. `kill $(lsof -i:5002 -t)`

### Key management:
The generation and sharing of the symmetric AES key is not part of the protocol. Data-holder parties have to agree on a shared key and safely exchange it via a secure side channel. The Linker should **never** receive the key.

## Demo scripts
To run a complete demo, open three separate terminal windows; for party 1, party 2 and the linker:
- Linker run: `cd Code/LINKER` and then `./scriptLinker.sh` and leave running
- Party 1 (ISTAT) run: `cd Code/ISTAT` and then `./scriptISTAT.sh` and wait for the message to press return (do not press return yet)
- Party 2 (BI) run: `cd Code/BI` and then `./scriptBI.sh` and wait for the message to press return, press return
- Party 1: also press return
- Party 2: if a process is still running (no prompt): press Ctrl-C to return to prompt
- Party 1 or 2: run queries, e.g. `cd ../SEND_QUERY` and then `python ./psiLinkerSendQuery.py 127.0.0.1 5002 "CLASSE_ETA, CLASSE_REDDITO" P2 3425245235`
- Linker: when parties are finished querying, press Ctrl-C to return to prompt


# Private Set Intersection with Typos

When the linkage variables are not unique or have typos, linkage errors may occur including false positives and false negatives, where a false positive is linking records from different units and a false negative is not linking records from the same unit. These errors mean that a unit may be errouneously included in the intersection or omitted from this intersection. They also mean that there may be some bias in a total derived from the obtained intersection. To deal with these errors, the protocol has been modified to estimate the linkage errors with a statistical model and to adjust for these errors when computing a total based on the intersection. See `psi_protocol_for_typos_notes.pdf` and the Readme file within the folder `Code/PSI_WITH_TYPOS` for further details on the protocol and the code, which is also available in the same folder.


# Simulations

Simulations were conducted to evaluate the modified protocol with typos, when performing exact comparisons of the linkage variables and when using Bloom filters. These simulations were conducted in R using the program `simulations.txt` in the folder `Code/SIMULATIONS`.



