This folder contains the code to create the 'distances vs TCRMatch thresholds' figure. The code is a little ad hoc and inefficient.

The script distance_vs_threshold.py is the main script, and it creates the results for regular hamming distances only.
To add the distance 1 + indels to the figure, I made a very ugly second script called distance_vs_threshold_indels.py that does just that.