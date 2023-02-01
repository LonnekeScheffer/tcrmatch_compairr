#!/bin/bash

iedb_input=$1
iedb_output=$2

# works with future version of compairr: only rename trimmed_seq to cdr3_aa

sed '1,1s/trimmed_seq/cdr3_aa/' $iedb_input > $iedb_output

