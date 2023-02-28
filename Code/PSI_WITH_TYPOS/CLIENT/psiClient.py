#! /usr/bin/python

import os
os.environ["R_HOME"] = r"C:\Program Files\R\R-4.1.1"

import rpy2
from rpy2.robjects import r
from rpy2.robjects.packages import importr
from rpy2.robjects.packages import STAP

import pandas as pd

import random
from time import time
import gmpy2
import hashlib
import urllib
import urllib.request
import json
import sys

e = 2**16+1  # e= 65537


def RSA_ENC(m, n):
    return pow(m, e, n)

# link_type=0 blocking
# link_type=1 link

print(sys.argv)
if len(sys.argv) == 7:
    IP = sys.argv[1]
    port = sys.argv[2]
    fileName = sys.argv[3]
    remoteKey = sys.argv[4]
    intersection = sys.argv[5]
    block_or_link = sys.argv[6]
else:
    print("IP,port,fileName,remoteKey,intersection")
    sys.exit(0)

block_or_link = block_or_link.strip()

if block_or_link == 'block':
    headerID  = 'block_key'
    link_type = 0
else:
    headerID  = 'link_key'
    link_type = 1


def hash_int(x):
    # returns an integer representation of a SHA256 digest of x
    return int(hashlib.sha256(str(x).encode()).hexdigest(), 16)


# read other party's public key (n)
fin = open(remoteKey)
n = fin.read()
n = int(n.strip())
print("n other party's public key", n)
fin.close()

# read client datafile first column from csv datafile (ID Keys)
fin = open(fileName, "r")
client_elements = [row.split(";")[link_type] for row in fin]
client_elements.pop(0)  # skip header row (column names)
fin.close()

# save a copy & convert to string
client_elements_clear = []
client_elements_clear[:] = client_elements[:]
for i in range(len(client_elements)):
    client_elements[i] = str(client_elements[i])

# get hashes for each ID Key
hashed_keys = [hash_int(i) for i in client_elements]

# print (client_elements_clear[:10])
# print (len(client_elements_clear))
# print (client_elements[:10])
# print (len(client_elements))
# print (hashed_keys[:10])
# print (len(hashed_keys))
# _ = input('waiting, press return')

# Create two lists with a length equal to nr. hashed ID Keys
# rs: random ints in the range of the public key n (0 < r < n+1)
# m_A: multiplications of an 'encryption of rs with server public key' and the hashed client ID-keys, mod n (converted to string)
m_A = [str(link_type)]
rs = []
for hashed_key in hashed_keys:
    r = random.randrange(n)
    rs.append(r)
    # multiply an 'encryption of r with server public key' and the hashed client ID-key, mod n
    obf = (RSA_ENC(r, n) * hashed_key) % n
    m_A.append(str(obf))

# print (rs[:10])
# print (m_A[:10])
# _ = input('waiting, press return')

# create URL request FORM body with params = comma seperated concatenation of all multiplications
params = urllib.parse.urlencode({'params': ",".join(m_A)})

# POST to server a list of H(IDKey_client) * RSA_ENC(r)
print("Sending records to server...")
params = params.encode('ascii')  # data should be bytes
req = urllib.request.Request('http://'+IP+':'+port, params)
with urllib.request.urlopen(req) as resp:
    response = resp.read()

print("##############")
print("response")
print("##############")
print("Received records from server!")
response = response.strip()
response = response.split(b"|")
print(response)
print("##############")

# get manipulated client elements back from server to compare for intersection: RSA_DEC_server(H(IDKey_client)) * r
client_elements = response[0].split(b",")
print("client_elements: ", len(client_elements))
for i in range(len(client_elements)):
    client_elements[i] = int(client_elements[i])
# for i in range(10):
#     print(client_elements[i])
# _ = input('response client elements  wait')

# get server elements from server to compare for intersection: H(RSA_DEC_server(H(IDKey_server)))
server_elements = response[1].split(b",")
print("serv_elements: ", len(server_elements))
for i in range(len(server_elements)):
    server_elements[i] = int(server_elements[i])
# for i in range(10):
#     print(server_elements[i])
# _ = input('response server elements  wait')

# multiply client elements by inverse of r to factor out r and hash the result
# H((RSA_DEC_server(H(IDKey_client)) * r) * inv_r) => H(RSA_DEC_server(H(IDKey_client)))
mymap = {}
for i in range(len(client_elements)):
    k = client_elements[i] = hash_int(
        (client_elements[i] * gmpy2.invert(rs[i], n)) % n)
    mymap[k] = i
client_elements[:10]

# determine the intersection by comparing client elements with server elements
# H(RSA_DEC_server(H(IDKey_client))) == H(RSA_DEC_server(H(IDKey_server))) ?

n_i = []
if link_type == 0:
    cnt = 0
    intersectionFile = open(intersection, 'w')
    intersectionFile.write(headerID + "\n")

for i in client_elements:
    # print(server_elements.count(i))
    n_i.append([server_elements.count(i)])
    if link_type == 0:
        if i in server_elements:
            # print mymap[i]
            # print(client_elements_clear[mymap[i]])
            intersectionFile.write(client_elements_clear[mymap[i]]+"\n")
            cnt += 1

if link_type == 0:
    print("common elements:", cnt)

all_nis_df  = pd.DataFrame(n_i,columns=["n_i"])
ni_freqs_df = all_nis_df.groupby(['n_i']).size().reset_index(name='freq')
ni_freqs_df.to_csv('ni_freqs.csv',index=False)    

# Call the R function to estimate the rates
with open('error_estimation_functions.txt', 'r') as f:
    string      = f.read()
    rlerror     = STAP(string, "rlerror")
    error_rates = rlerror.estimate_rates()
    #print(error_rates)

# bar_p = error_rates[0]
# bar_lambda = error_rates[1]
# rates_df  = pd.DataFrame([[bar_p,bar_lambda]],columns=["bar_p","bar_lambda"])

if link_type == 0:
    coverage = error_rates[0]
    bar_lambda = error_rates[1]
    rates_df  = pd.DataFrame([[coverage,bar_lambda]],columns=["coverage","bar_lambda"])
    rates_df.to_csv('blocking_rates.csv',index=False)
else:
    # Get the coverage
    b_rates = pd.read_csv('blocking_rates.csv')
    coverage = b_rates["coverage"][0]
    bar_p = error_rates[0]/coverage
    bar_lambda = error_rates[1]
    rates_df  = pd.DataFrame([[bar_p,bar_lambda]],columns=["bar_p","bar_lambda"])
    rates_df.to_csv('linking_rates.csv',index=False)

print(rates_df)


