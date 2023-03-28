#!/bin/bash

pipeline_version=6

iedb_input=/storage/lonnekes/TCRMatch_CompAIRR/data/IEDB_data.tsv
compairr_iedb_input=/storage/lonnekes/TCRMatch_CompAIRR/data/IEDB_for_compairr.tsv

infiles_folder=/storage/lonnekes/TCRMatch_CompAIRR/data/benchmarking_data
output_folder=/storage/lonnekes/TCRMatch_CompAIRR/benchmarking_v$pipeline_version

compairr_path=/storage/lonnekes/TCRMatch_CompAIRR/compairr/src/compairr
tcrmatch_path=/storage/lonnekes/TCRMatch_CompAIRR/TCRMatch/tcrmatch
compairr_tcrmatch_path=/storage/lonnekes/TCRMatch_CompAIRR/scripts/tcrmatch_compairr_pipeline.py

threshold=0.97


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
for n_seqs in 1e2 1e3 1e4 1e5
do

for implant_percentage in 0.1 1.0 10.0 100.0
do
benchmark_dataset=n$n_seqs\_p$implant_percentage
infile=$infiles_folder/$benchmark_dataset.tsv

for n_threads in 1 8
do

########################################################################
# TCRMatch benchmarking
unique_name=r$repetition\_$benchmark_dataset\_t$n_threads
echo $unique_name

out_subdir=$output_folder/tcrmatch_outfiles/tcrmatch/$unique_name
time_subdir=$output_folder/time/tcrmatch/$unique_name
mkdir $out_subdir
mkdir $time_subdir

(/usr/bin/time -f "exitcode %x\nuser     %U\nsystem   %S\nelapsed  %E\nmaxrss   %M" $tcrmatch_path -i $infile -a -t $n_threads -d $iedb_input -s $threshold > $out_subdir/tcrmatch_result.tsv) 2> $time_subdir/tcrmatch_time.txt
########################################################################

for differences in 1 2
do

for indels in 0 1
do

if [ $differences = 1 ] || [ $indels = 0 ]; then

########################################################################
# TCRMatch + CompAIRR benchmarking
unique_name=r$repetition\_$benchmark_dataset\_t$n_threads\_d$differences\_i$indels
echo $unique_name

out_subdir=$output_folder/tcrmatch_outfiles/compairr_tcrmatch/$unique_name
time_subdir=$output_folder/time/compairr_tcrmatch/$unique_name
mkdir $out_subdir
mkdir $time_subdir

if [ $indels = 1 ]; then
  indels_arg='-i'
else
  indels_arg=''
fi

(/usr/bin/time -f "exitcode %x\nuser     %U\nsystem   %S\nelapsed  %E\nmaxrss   %M" python3 $compairr_tcrmatch_path -u $infile -e $compairr_iedb_input -o $out_subdir/tcrmatch_result.tsv -d $differences -t $n_threads -s $threshold -c $compairr_path -m $tcrmatch_path -p $out_subdir/tmp -l $time_subdir/log.txt -z 100000 $indels_arg) 2> $time_subdir/compairr_tcrmatch_time.txt
########################################################################

fi
done
done
done
done
done
done