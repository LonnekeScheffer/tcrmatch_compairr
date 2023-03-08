#!/bin/bash

pipeline_version=3

iedb_input=/storage/lonnekes/TCRMatch_CompAIRR/data/IEDB_data.tsv
compairr_iedb_input=/storage/lonnekes/TCRMatch_CompAIRR/data/IEDB_for_compairr.tsv

infiles_folder=/storage/lonnekes/TCRMatch_CompAIRR/data/benchmarking_data
output_folder=/storage/lonnekes/TCRMatch_CompAIRR/benchmarking_v$pipeline_version

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

for repetition in 1 2 3
do
for n_seqs in 1e2 # 1e3 1e4 1e5 
do

for implant_percentage in 0.1 1.0 10.0
do
benchmark_dataset=n$n_seqs\_p$implant_percentage
infile=$infiles_folder/$benchmark_dataset.tsv

for n_threads in 1 8
do

# TCRMatch benchmarking
unique_name=r$repetition\_$benchmark_dataset\_t$n_threads

echo $unique_name
out_subdir=$output_folder/tcrmatch_outfiles/tcrmatch/$unique_name
time_subdir=$output_folder/time/tcrmatch/$unique_name
bash scripts/run_tcrmatch.sh $tcrmatch_path $iedb_input $infile $out_subdir $n_threads $time_subdir

for differences in 1 2
do

for indels in 0 1
do

if [ $differences = 1 ] || [ $indels = 0 ]; then
# TCRMatch + CompAIRR benchmarking
unique_name=r$repetition\_$benchmark_dataset\_t$n_threads\_d$differences\_i$indels
echo $unique_name
out_subdir=$output_folder/tcrmatch_outfiles/compairr_tcrmatch/$unique_name
time_subdir=$output_folder/time/compairr_tcrmatch/$unique_name
bash scripts/run_compairr_tcrmatch.sh $compairr_path $tcrmatch_path $compairr_iedb_input $infile $out_subdir $n_threads $time_subdir $differences $indels
fi

done

done

done
done
done
done