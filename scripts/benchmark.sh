#!/bin/bash

iedb_input=/storage/lonnekes/TCRMatch_CompAIRR/data/IEDB_data.tsv
compairr_iedb_input=/storage/lonnekes/TCRMatch_CompAIRR/data/IEDB_for_compairr.tsv

infiles_folder=/storage/lonnekes/TCRMatch_CompAIRR/data/infiles
output_folder=/storage/lonnekes/TCRMatch_CompAIRR/benchmarking

compairr_path=/storage/lonnekes/TCRMatch_CompAIRR/compairr/src/compairr
tcrmatch_path=/storage/lonnekes/TCRMatch_CompAIRR/TCRMatch/tcrmatch


if [ -d $output_folder ]
then
    rm -r $output_folder
fi

mkdir $output_folder
mkdir $output_folder/tcrmatch_outfiles
mkdir $output_folder/tcrmatch_outfiles/compairr_tcrmatch
mkdir $output_folder/tcrmatch_outfiles/tcrmatch
mkdir $output_folder/time
mkdir $output_folder/time/compairr_tcrmatch
mkdir $output_folder/time/tcrmatch

for repetition in 1 #2 3
do
for n_seqs in 10 #100 1000 # 10000
do
infile=$infiles_folder/infile_$n_seqs\_seqs.txt
for n_threads in 1 8
do

# TCRMatch benchmarking
unique_name=r$repetition\_n$n_seqs\_t$n_threads
echo $unique_name
outfile=$output_folder/tcrmatch_outfiles/tcrmatch/$unique_name.txt
time_folder=$output_folder/time/tcrmatch/$unique_name
bash scripts/run_tcrmatch.sh $tcrmatch_path $iedb_input $infile $outfile $n_threads $time_folder

for differences in 1 2
do

for indels in 0 1
do

if [ $differences = 1 ] || [ $indels = 0 ]; then
# TCRMatch + CompAIRR benchmarking
unique_name=r$repetition\_n$n_seqs\_t$n_threads\_d$differences\_i$indels
echo $unique_name
outfile=$output_folder/tcrmatch_outfiles/compairr_tcrmatch/$unique_name.txt
time_folder=$output_folder/time/compairr_tcrmatch/$unique_name
bash scripts/run_compairr_tcrmatch.sh $compairr_path $tcrmatch_path $compairr_iedb_input $infile $outfile $n_threads $time_folder $differences $indels
fi

done

done

done
done
done
