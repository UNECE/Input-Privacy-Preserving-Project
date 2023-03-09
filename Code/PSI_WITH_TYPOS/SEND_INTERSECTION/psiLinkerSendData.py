#! /usr/bin/python
import sys
import urllib.request
import urllib
import pandas as pd
import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
from AES.aes import AESCipher

print(sys.argv)
if len(sys.argv) == 7:
    IP = sys.argv[1]
    port = sys.argv[2]
    SymKey = sys.argv[3]
    fileName = sys.argv[4]
    intersection = sys.argv[5]
    user = sys.argv[6]
else:
    print("IP,port,SymKey,fileName,intersection,user")
    sys.exit(0)


def FromList2Mess(msglist, user, column_names):
    columnlist = []
    columnlist.append(user.encode('utf-8'))
    columnlist.append(b" ".join(column_names))
    for rowlist in msglist:
        columnlist.append(b" ".join(rowlist))
    msg = b"  ".join(columnlist)
    return msg


def colCript(column_names):
    colcript = []
    for w in column_names:
        colcript.append(aes.encrypt(w))
    return colcript


# symmetric shared key
aes = AESCipher(SymKey)

# read local dataset
df = pd.read_csv(fileName, sep=";")

# read the intersetion set ID's
df_i = pd.read_csv(intersection, sep=";")

unique_df_i = df_i.groupby('block_key').size().reset_index(name='count')

num_obs = unique_df_i.shape[0]
print("num_obs unique_df_i:",num_obs)

del unique_df_i['count']

# select just the intersected rows
column_names = df.columns.values.tolist()
DataIntersection = pd.merge(df, unique_df_i, how='inner',
                            left_on='block_key', right_on='block_key')[column_names]
df = DataIntersection
df = df.astype(str)

num_obs = df.shape[0]
print("num_obs:")
print(num_obs)

# print("dataset:")
# print(df)

# AES encrypt rows
dfcrypt = df.applymap(aes.encrypt)
msglist = dfcrypt.values.tolist()

# print("dataset:")
# print(df)
# print("encrypted:")
# print(dfcrypt)
# print("serialised:")
# print(msglist)

# AES encrypt column names
column_names_cript = colCript(column_names)

# create URL request FORM body with params = message containing user (e.g. P1, P2) + encrypted rows and columnames
params = urllib.parse.urlencode(
    {'params': FromList2Mess(msglist, user, column_names_cript)})

# send data to linker
params = params.encode('ascii')  # data should be bytes
req = urllib.request.Request('http://'+IP+':'+port, params)
with urllib.request.urlopen(req) as resp:
    response = resp.read()

print(response)
