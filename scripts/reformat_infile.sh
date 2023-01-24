#!/bin/bash

input=$1
output=$2

sed "s/$/\trepertoire_id/" $input | sed '1,1s/cdr3_aa/junction_aa/' > $output

