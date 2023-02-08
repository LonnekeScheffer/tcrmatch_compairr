#!/bin/bash

iedb_input=$1
iedb_output=$2

# rename 'trimmed_seq' to 'cdr3_aa' so it can be used as input for CompAIRR

sed '1,1s/trimmed_seq/cdr3_aa/' $iedb_input > $iedb_output

