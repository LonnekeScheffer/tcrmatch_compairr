#!/bin/bash

iedb_input=$1
iedb_output=$2

sed '1,1s/trimmed_seq/cdr3_aa/' $iedb_input > $iedb_output

# old version: removes some columns, but they need to be kept
#cut -f 1,4 $iedb_input | sed '1,1s/trimmed_seq/cdr3_aa/' > $iedb_output

# works with future version of compairr