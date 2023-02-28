
import os
os.environ["R_HOME"] = r"C:\Program Files\R\R-4.1.1"

import rpy2
from rpy2.robjects import r
from rpy2.robjects.packages import importr
from rpy2.robjects.packages import STAP

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
    return df, column[0]


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

            #--------------------------------#
            # read BI and ISTAT datafiles
            # from disk to seperate
            # dataframes and Linking
            # Key column names.
            # remember, all data is
            # encrypted (columnames &
            # datavalues)
            #--------------------------------#

            print("Party 1 data")
            dfP1, idKeyP1 = mkdf('LinkerP1.txt')
            print("Party 2 data")
            dfP2, idkeyP2 = mkdf('LinkerP2.txt')

            #--------------------------------#
            # create one joined dataframe
            # from both dataframes, join on
            # Key columns
            #--------------------------------#

            DataIntersection = pd.merge(
                dfP2, dfP1, how='inner', left_on=idKeyP1, right_on=idkeyP2)
            print(DataIntersection)
            print("server: query mode ----")

            #--------------------------------#
            # Estimate the linkage errors
            #--------------------------------#

            # Count the records in dfP1
            num_rows = dfP1.shape[0]

            # Compute the n_i's
            all_positive_nis_df   = DataIntersection.groupby(idKeyP1).size().reset_index(name='n_i')
            # all_positive_nis_df.rename(columns={'count':'n_i'})
            positive_nis_freqs_df = all_positive_nis_df.groupby(['n_i']).size().reset_index(name='freq')
            # positive_nis_freqs_df.rename(columns={'count':'freq'})
            num_wo_links          = num_rows - all_positive_nis_df.shape[0]
            if num_wo_links == 0:
                ni_freqs_df = positive_nis_freqs_df]
            else:
                nolinks_d   = {'n_i': [0], 'freq': [num_wo_links]}
                nolinks_df  = pd.DataFrame(data=nolinks_d)
                ni_freqs_df = pd.concat([nolinks_df,positive_nis_freqs_df])
            # display(ni_freqs_df)

            # Write the n_i freqencies to a text file
            ni_freqs_df.to_csv('ni_freqs.csv',index=False)

            # Call the R function to estimate the rates
            with open('error_estimation_functions.txt', 'r') as f:
                string      = f.read()
                rlerror     = STAP(string, "rlerror")
                error_rates = rlerror.estimate_rates()
                print(error_rates)

            #--------------------------------#
            # execute query: create aggregate
            # counts by grouping on query
            # column list
            #--------------------------------#

            resultdf = DataIntersection.groupby(
                query_columns).count()[idKeyP1].reset_index()
            columns = resultdf.columns
            print(columns.values)

            #--------------------------------#
            # create response message
            # containing: LINKER,
            # Column names, groupedby values
            # (all space separated)
            #--------------------------------#
            
            msglist = resultdf.values.tolist()
            m = FromList2Mess(msglist, 'LINKER', columns)
            print(str(m))

            return str(m)

        resp = 'no actions'
        return str(resp)


if __name__ == '__main__':
    app.run(host=IP, port=port)
