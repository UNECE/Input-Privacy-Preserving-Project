#! /usr/bin/python
from AES.aes import AESCipher
import urllib
import urllib.request
import sys
import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

print(sys.argv)
if len(sys.argv) == 6:
    IP = sys.argv[1]
    port = sys.argv[2]
    queryString = sys.argv[3]
    ClientName = sys.argv[4]
    SymKey = sys.argv[5]
else:
    print("IP,port,queryString,ClientName,SymKey")
    sys.exit(0)

print("QUERY MODE")


aes = AESCipher(SymKey)


def DecListStr(ListString):
    # decrypt a space-separated string of values to a semicolon-separated string of decrypted values: value1 value2 value3 --> decrypted1 ; decrypted2 ; decrypted 3
    l = []
    for fieldName in ListString.split(b" "):
        # print "@@@@@@@@@@@@@@@@@@@@"
        # print fieldName
        # print mydecrypt(fieldName)
        # print "@@@@@@@@@@@@@@@@@@@@"
        l.append(aes.decrypt(fieldName))
    return " ; ".join(l)


def mycryptQueryStr(queryString):
    # encrypt a comma-separated string of values to a space-separated string of encrypted values: value1,value2,value3 --> encrypted1 encrypted2 encrypted3
    l = []
    for field in queryString.split(','):
        # strip leading/trailing whitespace to prevent Linker errors (KeyNotFound)
        l.append(aes.encrypt(field.strip()))
    return b" ".join(l)


# create URL request FORM body with params = message containing type (QUERY), Clientname (user, e.g. P1, P2) + encrypted columnames to query
columnlist = []
columnlist.append(b"QUERY")
columnlist.append(ClientName.encode('utf-8'))
columnlist.append(mycryptQueryStr(queryString))
params = urllib.parse.urlencode({'params': b"  ".join(columnlist)})

# send query to linker
params = params.encode('ascii')  # data should be bytes
req = urllib.request.Request('http://'+IP+':'+port, params)
with urllib.request.urlopen(req) as resp:
    response = resp.read()
# print("--- resp: ----")
# print response

# decompose result into rows
# row 0 = LINKER
# row 1 = column names (encrypted)
# row 2..n = column values (encrypted groupby values, unencrypted aggregate counts)
rowlist = response.split(b"  ")

# print decrypted column names
print(DecListStr(rowlist[1]))

# iterate value rows
for fieldlist in rowlist[2:]:
    r = fieldlist.split(b" ")
    a = []
    for field_i in range(len(r)):
        if (field_i == len(r)-1):
            # last column contains unencrypted aggregate count
            a.append(str(r[field_i]))
        else:
            # other columns contain encrypted value -> decrypt
            a.append(str(aes.decrypt(r[field_i])))
    # print list of row values
    print(" ; ".join(a))

sys.exit(0)
