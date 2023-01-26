#!/bin/bash

iedb_input=$1
infile=$2
outfile=$3
threads=$4
time_folder=$5

tcrmatch_path=/storage/lonnekes/TCRMatch_CompAIRR/TCRMatch-1.0.2/tcrmatch


threshold=0.97


if [ -d $time_folder ]
then
    rm -r $time_folder
fi

mkdir $time_folder


(time $tcrmatch_path -i $infile -a -t $threads -d $iedb_input -s $threshold > $outfile) 2> $time_folder/tcrmatch_time.txt
