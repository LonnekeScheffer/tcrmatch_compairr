#!/bin/bash

compairr_path=$1
tcrmatch_path=$2
iedb_input=$3
infile=$4
outdir=$5
threads=$6
time_folder=$7
differences=$8
indels=$9
pipeline_version=${10}


tmp_folder=$outdir/tmp

pairs_file=$tmp_folder/pairs.tsv
compairr_log=$time_folder/compairr_log.txt
compairr_out=$tmp_folder/compairr_out.txt

threshold=0.97


if [ -d $time_folder ]
then
    rm -r $time_folder
fi

mkdir $outdir
mkdir $tmp_folder
mkdir $time_folder


if [ $indels = 1 ]; then
  indels_arg='--indels'
else
  indels_arg=''
fi

(/usr/bin/time -f "exitcode %x\nuser     %U\nsystem   %S\nelapsed  %E\nmaxrss   %M" $compairr_path $iedb_input $infile -m -d $differences $indels_arg --ignore-counts --ignore-genes --cdr3 -p $pairs_file -t $threads -l $compairr_log -o $compairr_out) 2> $time_folder/compairr_time.txt

if [ $pipeline_version = 1 ]; then
  outfile=$outdir/tcrmatch_result.tsv
  iedb_prefiltered=$tmp_folder/prefiltered_IEDB.tsv
  (/usr/bin/time -f "exitcode %x\nuser     %U\nsystem   %S\nelapsed  %E\nmaxrss   %M" python scripts/add_lost_cols_to_compairr_output.py --iedb_file $iedb_input --pairs_file $pairs_file --output_file $iedb_prefiltered) 2> $time_folder/fileprocessing_time.txt
  (/usr/bin/time -f "exitcode %x\nuser     %U\nsystem   %S\nelapsed  %E\nmaxrss   %M" $tcrmatch_path -i $infile -a -t $threads -d $iedb_prefiltered -s $threshold > $outfile) 2> $time_folder/tcrmatch_time.txt
elif [ $pipeline_version = 2 ]; then
  (/usr/bin/time -f "exitcode %x\nuser     %U\nsystem   %S\nelapsed  %E\nmaxrss   %M" python scripts/add_lost_cols_to_compairr_output.py --iedb_file $iedb_input --pairs_file $pairs_file --split_output --output_folder $tmp_folder) 2> $time_folder/fileprocessing_time.txt
  (/usr/bin/time -f "exitcode %x\nuser     %U\nsystem   %S\nelapsed  %E\nmaxrss   %M" bash scripts/run_tcrmatch_loop.sh $tcrmatch_path $threads $threshold $tmp_folder $outdir) 2> $time_folder/tcrmatch_time.txt
fi

rm -r $tmp_folder