#!/bin/bash

iedb_input=/storage/lonnekes/TCRMatch_CompAIRR/data/IEDB_for_compairr.tsv

for repetition in 1 2 3
do
for n_seqs in 10 100 1000 10000
do
infile=/storage/lonnekes/TCRMatch_CompAIRR/data/infiles/infile_$n_seqs\_seqs.txt
for n_threads in 1 8
do
for differences in 1 2
do
unique_name=r$repetition\_n$n_seqs\_t$n_threads\_d$differences
echo $unique_name
outfile=/storage/lonnekes/TCRMatch_CompAIRR/tcrmatch_outfiles/compairr_tcrmatch/$unique_name.txt
time_folder=/storage/lonnekes/TCRMatch_CompAIRR/time/compairr_tcrmatch/$unique_name
bash scripts/run_compairr_tcrmatch.sh $iedb_input $infile $outfile $n_threads $time_folder $differences
done
done
done
done
