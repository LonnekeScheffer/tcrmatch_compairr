#!/bin/bash

tcrmatch_path=$1
iedb_input=$2
infile=$3
out_dir=$4
threads=$5
time_dir=$6

outfile=$out_dir/tcrmatch_result.tsv

threshold=0.97


if [ -d $time_dir ]
then
    rm -r $time_dir
fi

mkdir $time_dir
mkdir $out_dir

(/usr/bin/time -f "exitcode %x\nuser     %U\nsystem   %S\nelapsed  %E\nmaxrss   %M" $tcrmatch_path -i $infile -a -t $threads -d $iedb_input -s $threshold > $outfile) 2> $time_dir/tcrmatch_time.txt
