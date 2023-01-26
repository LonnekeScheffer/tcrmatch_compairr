#!/bin/bash

compairr_path=$1
iedb_input=$2
infile=$3
iedb_output=$4
differences=$5
threads=$6
#tmp_file=tmp.tsv


$compairr_path $iedb_input $infile -m -d $differences --ignore-counts --ignore-genes -p $iedb_output -t $threads

# todo in final version: column 2 is not necessary, an epitope column is added, and perhaps the junction_aa from the

#cut -f 2,6 $tmp_file > $iedb_output
#rm $tmp_file