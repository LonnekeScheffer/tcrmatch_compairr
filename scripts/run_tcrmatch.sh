#!/bin/bash

#/storage/lonnekes/TCRMatch_CompAIRR/TCRMatch-1.0.2/tcrmatch

tcrmatch_path=$1
iedb_input=$2
infile=$3
outfile=$4
threads=$5
time_folder=$6


threshold=0.97


if [ -d $time_folder ]
then
    rm -r $time_folder
fi

mkdir $time_folder


(/usr/bin/time -f "exitcode %x\nuser     %U\nsystem   %S\nelapsed  %E\nmaxrss   %M" $tcrmatch_path -i $infile -a -t $threads -d $iedb_input -s $threshold > $outfile) 2> $time_folder/tcrmatch_time.txt
