#!/bin/bash

tcrmatch_path=$1
pairs_subset_file=$2
tmp_dir=$3
threshold=$4
tcrmatch_outfile=$5



# loop through each line of the pairs subset file
COUNTER=0
while IFS=$'\t' read -r input_cdr3 trimmed_seq original_seq receptor_group epitopes source_organisms source_antigens
do
  single_input_filename=$tmp_dir/input_cdr3_$COUNTER.txt
  single_iedb_filename=$tmp_dir/iedb_cdr3_$COUNTER.txt
  single_tcrmatch_output=$tmp_dir/tcrmatch_output_$COUNTER.txt

  # make tmp files with 1 user CDR3 and 1 IEDB CDR3
  echo $input_cdr3 > $single_input_filename
  echo -e 'trimmed_seq\toriginal_seq\treceptor_group\tepitopes\tsource_organisms\tsource_antigens\n'$trimmed_seq'\t'$original_seq'\t'$receptor_group'\t'$epitopes'\t'$source_organisms'\t'$source_antigens > $single_iedb_filename

  # run TCRMatch on single entry
  $tcrmatch_path -i $single_input_filename -t 1 -d $single_iedb_filename -s $threshold > $single_tcrmatch_output

  # get the header from the first tcrmatch outfile
  if [ $COUNTER = 0 ]; then
    head -n 1 $single_tcrmatch_output > $tcrmatch_outfile
  fi

  # skip header and append file content
  tail -n +2 $single_tcrmatch_output >> $tcrmatch_outfile

  rm $single_input_filename $single_iedb_filename $single_tcrmatch_output
  let COUNTER=COUNTER+1
done < $pairs_subset_file