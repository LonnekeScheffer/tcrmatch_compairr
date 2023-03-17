#!/bin/bash

pairs_file=$1
iedb_subsets_dir=$2
tmp_dir=$3



mkdir $iedb_subsets_dir

awk -v FS='\t' -v OFS='\t' -v user_seq="cdr3_aa_2" -v trimmed_seq="cdr3_aa_1" -v original_seq="original_seq_1" -v receptor_group="receptor_group_1" -v epitopes="epitopes_1" -v source_organisms="source_organisms_1" -v source_antigens="source_antigens_1" -v iedb_subsets_dir="$iedb_subsets_dir/" 'NR==1{for(i=1;i<=NF;i++){if($i==user_seq)c1=i; if($i==trimmed_seq)c2=i; if ($i==original_seq)c3=i; if ($i==receptor_group)c4=i; if ($i==epitopes)c5=i; if ($i==source_organisms)c6=i; if ($i==source_antigens)c7=i;}} NR>1{ fname = iedb_subsets_dir $c1 ; print $c2, $c3, $c4, $c5, $c6, $c7 > fname }' $pairs_file


mkdir $tmp_dir


COUNTER=1
for iedb_subset_file in $iedb_subsets_dir/*;
do
  curr_iedb_file=$tmp_dir/prefiltered_IEDB_$COUNTER.tsv
  curr_cdr3_file=$tmp_dir/user_cdr3_$COUNTER.txt

  # make partial IEDB file with header
  echo -e "trimmed_seq\toriginal_seq\treceptor_group\tepitopes\tsource_organisms\tsource_antigens" > $curr_iedb_file && cat $iedb_subset_file >> $curr_iedb_file

  # user CDR3 file
  basename "$iedb_subset_file" > $curr_cdr3_file

  let COUNTER=COUNTER+1
done

