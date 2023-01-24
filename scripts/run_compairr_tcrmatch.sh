#!/bin/bash

iedb_input=$1
infile=$2
compairr_path=compairr
tcrmatch_path=tcrmatch
infile_compairr=tmp/infile_compairr.tsv
iedb_prefiltered=tmp/prefiltered_IEDB.tsv
pairs_file=tmp/pairs.tsv

differences=1
threads=1
threshold=0.97



mkdir tmp

sed "s/$/\trepertoire_id/" $infile | sed '1,1s/cdr3_aa/junction_aa/' > $infile_compairr
$compairr_path $iedb_input $infile -m -d $differences --ignore-counts --ignore-genes -p $iedb_output -t $threads
python scripts/add_lost_cols_to_compairr_output.py --iedb_file $iedb_input --pairs_file $pairs_file --output_file $iedb_prefiltered


# todo optional: splitting IEDB

#rm -r tmp

$tcrmatch_path -i $infile -a -t $threads -d $iedb_prefiltered -s $threshold




# old version: running scripts
#bash scripts/reformat_infile.sh $infile $infile_compairr
#bash scripts/prefilter_iedb_with_compairr.sh $compairr_path $iedb_input $infile_compairr $pairs_file $differences $threads
#python scripts/add_lost_cols_to_compairr_output.py --iedb_file $iedb_input --pairs_file $pairs_file --output_file $iedb_prefiltered
