#!/bin/bash

iedb_input=$1
iedb_output=$2

awk '{printf "%s\t%s\t%s\n", NR-1,1,$0}' $iedb_input | # add sequence_id & repertoire_id columns
sed '1,1s/0/sequence_id/' | sed '1,1s/1/repertoire_id/' |  # rename cols 0 & 1 to sequence_id & repertoire_id
sed '1,1s/trimmed_seq/junction_aa/' > $iedb_output # rename col trimmed_seq to junction_aa

# works with current version of compairr (1.9.0): needs junction_aa field instead of cdr3_aa field, and repertoire_id