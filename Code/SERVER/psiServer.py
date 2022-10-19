#!/usr/bin/python
###SERVER###
import random
import sys
from time import time
import gmpy2
import hashlib
from flask import Flask
from flask import request

e = 2**16+1  # e= 65537

app = Flask(__name__)

print(sys.argv)
if len(sys.argv) == 5:
    IP = sys.argv[1]
    port = sys.argv[2]
    fileName = sys.argv[3]
    publicKey = sys.argv[4]
else:
    print("IP,port,fileName,publicKey")
    sys.exit(0)


def hash_int(x):
    # returns an integer representation of a SHA256 digest of x
    return int(hashlib.sha256(str(x).encode()).hexdigest(), 16)


def gen_prime(BIT_LEN):
    # generates a random prime of the requested bit length
    print("gen_prime")
    found = False
    while found == False:
        p = random.randrange(2**(BIT_LEN - 1), 2**BIT_LEN)
        found = gmpy2.is_prime(p)
    return p


def gen_safe_prime(BIT_LEN):
    # generates a random safe prime of the requested bit length
    print("gen_safe_prime")
    found = False
    while found == False:
        q = random.randrange(2**(BIT_LEN - 2), 2**(BIT_LEN - 1))
        p = 2 * q + 1
        found = gmpy2.is_prime(p) and gmpy2.is_prime(q)
    return p


def RSA_GEN(BIT_LEN):
    print("RSA_GEN")

    # this is faster but not so secure as gen_safe_prime
    p = gen_prime(BIT_LEN)
    q = gen_prime(BIT_LEN)
    # p=gen_safe_prime(BIT_LEN)
    # q=gen_safe_prime(BIT_LEN)

    n = p * q
    f = (p-1) * (q-1)
    e = 2**16 + 1
    d = gmpy2.invert(e, f)
    return d, n


def RSA_DEC(c, d, n):
    return pow(c, d, n)


@app.route('/', methods=['POST'])
def process_request():
    print("process_request")
    if request.method == 'POST':
        print("processing POST request...")

        vals = request.form['params']
        print("Client values received")
        print(vals[:100])
        # _ = input('waiting, press return')
        client_elements = vals.split(",")
        for i in range(len(client_elements)):
            client_elements[i] = int(client_elements[i])

        # first part of response = list of RSA_DEC(H(IDKey_client) * RSA_ENC(r)) = list of RSA_DEC(H(IDKey_client)) * r
        m_B1 = [RSA_DEC(x, d, n) for x in client_elements]
        print(m_B1[0])
        # _ = input('waiting, press return')

        # get hashes for each Server ID Key
        hashed_server_keys = [hash_int(i) for i in server_elements]
        # second part of response = list of H(RSA_DEC(H(IDKey_server)))
        m_B2 = [hash_int(RSA_DEC(y, d, n)) for y in hashed_server_keys]

        print("sending response...")

        client_enc = ""
        for cc in m_B1:
            client_enc += str(cc) + ","
        client_enc = client_enc[:-1]
        srv_enc = ""
        for cc in m_B2:
            srv_enc += str(cc) + ","
        srv_enc = srv_enc[:-1]
        resp = client_enc + "|" + srv_enc

        return str(resp)


if __name__ == '__main__':
    # generate RSA key pair (public n,private d) for the server
    d, n = RSA_GEN(512)
    # print (n)
    # print (d)

    # write public key n to file
    fout = open(publicKey, "w")
    fout.write(str(n))
    fout.close()

    # read server datafile first column from csv datafile (ID Keys)
    fin = open(fileName, "r")
    server_elements = [row.split(";")[0] for row in fin]
    # server_elements.pop(0) # skip header row (column names)
    fin.close()

    # convert to string
    for i in range(len(server_elements)):
        server_elements[i] = str(server_elements[i])
    # print (server_elements[:10])
    # _ = input('waiting, press return')

    app.run(host=IP, port=port)
