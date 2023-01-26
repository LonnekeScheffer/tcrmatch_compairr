#!/bin/bash

iedb_input=$1
infile=$2
outfile=$3
threads=$4
time_folder=$5
differences=$6

#compairr_path=/storage/lonnekes/TCRMatch_CompAIRR/compairr/src/compairr
compairr_path=compairr
tcrmatch_path=/storage/lonnekes/TCRMatch_CompAIRR/TCRMatch-1.0.2/tcrmatch

tmp_folder=tmp

infile_compairr=$tmp_folder/infile_compairr.tsv
iedb_prefiltered=$tmp_folder/prefiltered_IEDB.tsv
pairs_file=$tmp_folder/pairs.tsv
compairr_log=$time_folder/compairr_log.txt
compairr_out=$tmp_folder/compairr_out.txt

threshold=0.97


if [ -d $tmp_folder ]
then
    rm -r $tmp_folder
fi

if [ -d $time_folder ]
then
    rm -r $time_folder
fi

mkdir $tmp_folder
mkdir $time_folder

sed "s/$/\trepertoire_id/" $infile | sed '1,1s/cdr3_aa/junction_aa/' > $infile_compairr
(time $compairr_path $iedb_input $infile_compairr -m -d $differences --ignore-counts --ignore-genes -p $pairs_file -t $threads -l $compairr_log -o $compairr_out) 2> $time_folder/compairr_time.txt
(time python scripts/add_lost_cols_to_compairr_output.py --iedb_file $iedb_input --pairs_file $pairs_file --output_file $iedb_prefiltered) 2> $time_folder/compairr_postprocess_time.txt

# todo optional: splitting IEDB

(time $tcrmatch_path -i $infile -a -t $threads -d $iedb_prefiltered -s $threshold > $outfile) 2> $time_folder/tcrmatch_time.txt

rm -r tmp
