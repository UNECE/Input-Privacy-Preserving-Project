#! /usr/bin/python
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


print(sys.argv)
if len(sys.argv) == 6:
    IP = sys.argv[1]
    port = sys.argv[2]
    fileName = sys.argv[3]
    remoteKey = sys.argv[4]
    intersection = sys.argv[5]
else:
    print("IP,port,fileName,remoteKey,intersection")
    sys.exit(0)

headerID = 'IDKEY'


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
client_elements = [row.split(";")[0] for row in fin]
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
m_A = []
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
cnt = 0
intersectionFile = open(intersection, 'w')
intersectionFile.write(headerID + "\n")
for i in client_elements:
    if i in server_elements:
        # print mymap[i]
        print(client_elements_clear[mymap[i]])
        intersectionFile.write(client_elements_clear[mymap[i]]+"\n")
        cnt += 1
print("common elements:", cnt)
