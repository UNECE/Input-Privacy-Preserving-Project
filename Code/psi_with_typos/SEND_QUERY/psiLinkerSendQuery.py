#! /usr/bin/python
import pandas as pd
import urllib
import urllib.request
import sys
import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
from AES.aes import AESCipher

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

response = response.split(b"|")

block_rowlist = response[0].split(b"  ")
link_rowlist  = response[1].split(b"  ")

# print decrypted column names
column_names = DecListStr(block_rowlist[1])
column_names.strip()
# print(column_names)

column_names = column_names.split(";")
num_vars     = len(column_names)
column_list = [[] for x in range(num_vars)]

# iterate value rows
for fieldlist in block_rowlist[2:]:
    r = fieldlist.split(b" ")
    a = []
    for field_i in range(len(r)):
        if (field_i == len(r)-1):
            # last column contains unencrypted aggregate count
            a.append(str(r[field_i]))
            column_list[field_i].append(str(r[field_i]))
        else:
            # other columns contain encrypted value -> decrypt
            a.append(str(aes.decrypt(r[field_i])))
            column_list[field_i].append(str(aes.decrypt(r[field_i])))
    # print list of row values
    # print(" ; ".join(a))

block_df_t = pd.DataFrame(column_list)
block_df   = block_df_t.transpose()
column_names[2] = "b_count"
block_df.columns = column_names
block_df['b_count'] = block_df['b_count'].apply(lambda a: a.replace("b'",""))
block_df['b_count'] = block_df['b_count'].apply(lambda a: a.replace("'",""))
block_df = block_df.astype({"b_count": int})

print(block_df)

column_list = [[] for x in range(num_vars)]

# print decrypted column names
# print(DecListStr(link_rowlist[1]))

# iterate value rows
for fieldlist in link_rowlist[2:]:
    r = fieldlist.split(b" ")
    a = []
    for field_i in range(len(r)):
        if (field_i == len(r)-1):
            # last column contains unencrypted aggregate count
            a.append(str(r[field_i]))
            column_list[field_i].append(str(r[field_i]))
        else:
            # other columns contain encrypted value -> decrypt
            a.append(str(aes.decrypt(r[field_i])))
            column_list[field_i].append(str(aes.decrypt(r[field_i])))
    # print list of row values
    # print(" ; ".join(a))

link_df_t = pd.DataFrame(column_list)
link_df   = link_df_t.transpose()
link_df.columns = column_names
link_df = link_df.rename(columns={'b_count': 'l_count'})
link_df['l_count'] = link_df['l_count'].apply(lambda a: a.replace("b'",""))
link_df['l_count'] = link_df['l_count'].apply(lambda a: a.replace("'",""))
link_df = link_df.astype({"l_count": int})

print(link_df)

queryString = queryString.strip()
split_queryString  = queryString.split(",")
num_query_vars = len(split_queryString)

#query_vars = []
#for i in range(num_query_vars):
#    query_vars.append(split_queryString[i].replace("'","""))

vars = list(block_df)
del vars[-1]

merged_df = pd.merge(block_df, link_df, how="inner", on=vars)

#print(merged_df)

b_rates = pd.read_csv('blocking_rates.csv')
l_rates = pd.read_csv('linking_rates.csv')

b_bar_lambda = b_rates["bar_lambda"][0]

l_bar_p = l_rates["bar_p"][0]
l_bar_lambda = l_rates["bar_lambda"][0]

corrected_count = (merged_df["l_count"]-(l_bar_lambda/b_bar_lambda)*merged_df["b_count"])/(l_bar_p - (l_bar_lambda/b_bar_lambda))

final_df = merged_df.assign(corrected_count=corrected_count)

print(final_df)

#print(b_rates)
#print(l_rates)

sys.exit(0)

