
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

