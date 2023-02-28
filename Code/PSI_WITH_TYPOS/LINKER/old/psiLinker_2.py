
import pandas as pd
from flask import Flask
from flask import request
import sys


print(sys.argv)
if len(sys.argv) == 3:
    IP = sys.argv[1]
    port = sys.argv[2]
else:
    print("IP,port")
    sys.exit(0)

app = Flask(__name__)


def Stream2List(text):
    data = []
    for row in text.split("  ")[:4]:
        data.append(row.split(" "))
    return data


def mkdf(nomeFile_df):
    LinkerFile = open(nomeFile_df, 'r')
    text = LinkerFile.readline()
    LinkerFile.close()

    d = []
    for row in text.split("  "):
        d.append(row.split(" "))

    column = d[1]
    print("column", column)
    print(d[2])

    df = pd.DataFrame(d[2:], columns=column)
    return df, column[0], column[1]


def FromList2Mess(msglist, user, columns):
    columnlist = []
    columnlist.append(user)
    columnlist.append(" ".join(columns))
    for rowlist in msglist:
        s = []
        for ss in rowlist:
            s.append(str(ss))
        columnlist.append(" ".join(s))
    msg = "  ".join(columnlist)
    return msg


@app.route('/', methods=['POST'])
def hello_world():
    if request.method == 'POST':

        vals = request.form['params']
        print("Client values received")
        data = Stream2List(vals)
        print("--------------")
        print(data[0])
        print(data[1])
        print(data[2])
        print("--------------")

        # save party 1 dataset to disk and exit
        if (data[0][0] == 'P1'):
            LinkerP1 = open('LinkerP1.txt', 'w')
            LinkerP1.write(vals)
            LinkerP1.close()
            return ("Welcome Party 1")

        # or... save party 2 dataset to disk and exit
        if (data[0][0] == 'P2'):
            LinkerP2 = open('LinkerP2.txt', 'w')
            LinkerP2.write(vals)
            LinkerP2.close()
            return ("Welcome Party 2")

        # or... execute query and return results
        if (data[0][0] == 'QUERY'):
            print("-------- SERVER QUERY ----------")
            query_columns = data[2]
            print(query_columns)
            print("----#####---------")

            # read BI and ISTAT datafiles from disk to seperate dataframes and Linking Key column names.
            # remember, all data is encrypted (columnames & datavalues)
            print("Party 1 data")
            dfP1, block_KeyP1, link_KeyP1 = mkdf('LinkerP1.txt')
            print("Party 2 data")
            dfP2, block_KeyP2, link_KeyP2 = mkdf('LinkerP2.txt')

            # create one joined dataframe from both dataframes, join on Key columns
            block_DataIntersection = pd.merge(
                dfP2, dfP1, how='inner', left_on=block_KeyP1, right_on=block_KeyP2)
            print(block_DataIntersection)
            
            link_DataIntersection = pd.merge(
                dfP2, dfP1, how='inner', left_on=link_KeyP1, right_on=link_KeyP2)
            print(link_DataIntersection)

            print("server: query mode ----")

            # execute query: create aggregate counts by grouping on query column list
            block_resultdf_0 = block_DataIntersection.groupby(
                query_columns).count()[block_KeyP1].reset_index()

            num_rows  = block_resultdf_0.shape[0]
            link_type = ['block' for x in range(num_rows)]
            block_resultdf = block_resultdf_0.assign(link_type=link_type)

            link_resultdf_0 = link_DataIntersection.groupby(
                query_columns).count()[link_KeyP1].reset_index()

            num_rows  = link_resultdf_0.shape[0]
            link_type = ['link' for x in range(num_rows)]
            link_resultdf = link_resultdf_0.assign(link_type=link_type)

            resultdf = pd.concat([block_resultdf, link_resultdf])
            
            columns = resultdf.columns
            print(columns.values)

            # create response message containing: LINKER, Column names, groupedby values (all space separated)
            msglist = resultdf.values.tolist()
            m = FromList2Mess(msglist, 'LINKER', columns)
            print(str(m))

            return str(m)

        resp = 'no actions'
        return str(resp)


if __name__ == '__main__':
    app.run(host=IP, port=port)
