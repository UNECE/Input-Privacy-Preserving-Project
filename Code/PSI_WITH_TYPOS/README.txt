
The modified protocol is

The modified protocol assumes that there is a perfect blocking key. In this protocol the two datasets are linked twice by the deterministic method of record linkage. In the first linkage the blocking key is used. In the second linkage, another more restrictive linkage key is used, which is obtained by concatenating the blocking key with additional variables. The blocking key is used to determine the intersection of the two datasets. Each client estimates the coverage of the other dataset and the rates of linkage error when linking with the blocking key and the more restrictive key, including the recall and the false positive rate. Note that for the blocking key, only the false positive rate is measured because the blocking key is assumed to be perfect, i.e. a recall of 1.0. When the linker receives a query to compute some aggregates, it links the two datasets twice with the deterministic method, once with the blocking key and once with the more restrictive linkage key, to produce two estimates of each aggregate. These estimates are sent to the requesting client that computes the corrected estimates, which adjust for the linkage errors. 

The code can be tested using two pairs of datasets, which were produced by modifying the datasets with 100K records provided by Loe, i.e. "Statcan imp data.csv" and "Cbs exp data FUZZY.csv". The first pair of datasets comprises the datasets "cbs_exp_data_fuzzy.txt" and "statcan_imp_data.txt". This first pair corresponds to the situation where two censuses must be linked. The second pair of datasets comprises the datasets "cbs_exp_data_fuzzy_sample.txt" and "statcan_imp_data_sample.txt", which are obtained by drawing a Bernoulli sample with probability 0.7 from each dataset in the first pair. The dataset "statcan_imp_data.txt" is obtained by adding the variables block_key and link_key to the dataset "Statcan imp data.csv", where block_key is obtained by concatenating the variables exp_id and hs6, and link_key is obtained by concatenating the variables exp_id,hs6,date and value. The dataset "cbs_exp_data_fuzzy.txt" is obtained from "Cbs exp data FUZZY.csv" by only keeping the correct hs6 value for all the records, i.e. the variable hs6 is dropped and the variable hs6_correct is renamed to hs6. For the transaction date and value, the correct values are used with probability 0.8. Otherwise the perturbed values are used.

To test the code with cbs_exp_data_fuzzy.txt and statcan_imp_data.txt apply the steps below. When using cbs_exp_data_fuzzy_sample.txt and statcan_imp_data_sample.txt simply replace cbs_exp_data_fuzzy.txt with cbs_exp_data_fuzzy_sample.txt and statcan_imp_data.txt with statcan_imp_data_sample.txt, in the instructions. The code is barebone with minimum handling of errors and exceptions. This is left for future work.

Start the linker
================

Open a DOS window, go to the LINKER folder (within the psi_with_typos folder) and submit the following command.

python psiLinker.py 127.0.0.1 5002

Start the CBS server
====================

Open a new DOS window (CBS server window), go to the CBS folder (within the psi_with_typos folder) and submit the following command.

python ../SERVER/psiServer.py 127.0.0.1 5001 ./cbs_exp_data_fuzzy.txt ../PUBLIC_KEYS/CBSkey&

Start the STATCAN server
========================

Open a new DOS window (STATCAN server window), go to the CBS folder (within the psi_with_typos folder) and submit the following command.

python ../SERVER/psiServer.py 127.0.0.1 5000 ./statcan_imp_data.txt ../PUBLIC_KEYS/STATCANkey&

CBS determines the intersection based on the blocking key
=========================================================

In this step, CBS determines the intersection of its dataset with STATCAN dataset based on the blocking key. The result of this comparison is saved in the file "intersectionCBS.txt". CBS estimates the coverage of STATCAN dataset, i.e. the probability that a unit/transaction is included in STATCAN dataset while assuming a uniform inclusion probability. It also estimates the false positive rate when linking based on the blocking criterion. To implement this step, open a new DOS window (CBS client window), go to the CBS folder and submit the following command  where the key word "block" is used to signal that the blocking key is to be used.

python ../CLIENT/psiClient.py  127.0.0.1 5000 ./cbs_exp_data_fuzzy.txt ../PUBLIC_KEYS/STATCANkey intersectionCBS.txt block

CBS estimates the error rates when linking with the linkage key
===============================================================

CBS estimates the error rates when linking with the linkage key. However no intersection file is created. To implement this step, in the CBS client window, submit the following command, where the key word "link" signals that the linkage key is to be used.

python ../CLIENT/psiClient.py  127.0.0.1 5000 ./cbs_exp_data_fuzzy.txt ../PUBLIC_KEYS/STATCANkey none link

STATCAN determines the intersection based on the blocking key
=============================================================

In this step, STATCAN determines the intersection of its dataset with CBS dataset based on the blocking key. The result of this comparison is saved in the file "intersectionSTATCAN.txt". STATCAN estimates the coverage of CBS dataset, i.e. the probability that a unit/transaction is included in CBS dataset while assuming a uniform inclusion probability. It also estimates the false positive rate when linking based on the blocking criterion. To implement this step, open a new DOS window (STATCAN client window), go to the STATCAN folder and submit the following command  where the key word "block" signals that the blocking key is to be used.

python ../CLIENT/psiClient.py  127.0.0.1 5001 ./statcan_imp_data.txt ../PUBLIC_KEYS/CBSkey intersectionSTATCAN.txt block

STATCAN estimates the error rates when linking with the linkage key
===================================================================

STATCAN estimates the error rates when linking with the linkage key. However no intersection file is created. To implement this step, in the STATCAN client window, submit the following command, where the key word "link" signals that the linkage key is to be used.

python ../CLIENT/psiClient.py  127.0.0.1 5001 ./statcan_imp_data.txt ../PUBLIC_KEYS/CBSkey none link

STATCAN sends its intersection dataset to the linker
====================================================

python ../SEND_INTERSECTION/psiLinkerSendData.py 127.0.0.1 5002 3425245235 ./statcan_imp_data.txt ./intersectionSTATCAN.txt P1

CBS sends its intersection dataset to the linker
================================================

python ../SEND_INTERSECTION/psiLinkerSendData.py 127.0.0.1 5002 3425245235 ./cbs_exp_data_fuzzy.txt ./intersectionCBS.txt P2

CBS makes a query to the linker
===============================

python ../SEND_QUERY/psiLinkerSendQuery.py 127.0.0.1 5002 "exp_size,pref_kode" P2 3425245235


Obtain the following output in the CBS client window where b_count is the blocking estimate, l_count is the estimate based on the linkage key. It shows three tables. The first table gives the b_count for each cross-classification of the query variables. The second table gives the l_count for each cross-classification of the query variables. The third table is based on merging the first two tables. It also includes the corrected count based on the estimated error rates.

  exp_size   pref_kode   b_count
0     small         100   139049
1     small         300    46795
2     large         100   159037
3     large         300    52261

  exp_size   pref_kode   l_count
0     small         100    28194
1     small         300     9612
2     large         100    31595
3     large         300    10416

  exp_size   pref_kode   b_count  l_count  corrected_count
0     small         100   139049    28194     35326.844527
1     small         300    46795     9612     12043.755041
2     large         100   159037    31595     39588.268876
3     large         300    52261    10416     13051.160267

When using the samples cbs_exp_data_fuzzy_sample.txt and statcan_imp_data_sample.txt, obtain the following output in the CBS client window.

  exp_size   pref_kode   b_count
0     small         100    68677
1     small         300    22951
2     large         100    77687
3     large         300    25910

  exp_size   pref_kode   l_count
0     small         100    14013
1     small         300     4649
2     large         100    15377
3     large         300     5185

  exp_size   pref_kode   b_count  l_count  corrected_count
0     small         100    68677    14013     17345.776840
1     small         300    22951     4649      5754.693251
2     large         100    77687    15377     19034.183290
3     large         300    25910     5185      6418.172619