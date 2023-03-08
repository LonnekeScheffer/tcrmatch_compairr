#!/bin/bash

compairr_path=$1
tcrmatch_path=$2
iedb_input=$3
infile=$4
out_dir=$5
threads=$6
time_dir=$7
differences=$8
indels=$9
pipeline_version=3

tmp_dir=$out_dir/tmp

pairs_file=$tmp_dir/pairs.tsv
pairs_subset_file=$tmp_dir/pairs_subset.tsv
compairr_log=$time_dir/compairr_log.txt
compairr_out=$tmp_dir/compairr_out.txt
tcrmatch_outfile=$out_dir/tcrmatch_result.tsv

threshold=0.97

if [ -d $time_dir ]
then
    rm -r $time_dir
fi

mkdir $out_dir
mkdir $tmp_dir
mkdir $time_dir


if [ $indels = 1 ]; then
  indels_arg='--indels'
else
  indels_arg=''
fi

# run compairr and make pairs file
(/usr/bin/time -f "exitcode %x\nuser     %U\nsystem   %S\nelapsed  %E\nmaxrss   %M" $compairr_path $iedb_input $infile -m -d $differences $indels_arg --ignore-counts --ignore-genes --cdr3 -p $pairs_file -t $threads -l $compairr_log -o $compairr_out --keep-columns original_seq,receptor_group,epitopes,source_organisms,source_antigens) 2> $time_dir/compairr_time.txt


# keep only relevant columns and no header of pairs file
(/usr/bin/time -f "exitcode %x\nuser     %U\nsystem   %S\nelapsed  %E\nmaxrss   %M" awk -v FS='\t' -v OFS='\t' -v user_seq="cdr3_aa_2" -v trimmed_seq="cdr3_aa_1" -v original_seq="original_seq_1" -v receptor_group="receptor_group_1" -v epitopes="epitopes_1" -v source_organisms="source_organisms_1" -v source_antigens="source_antigens_1" 'NR==1{for(i=1;i<=NF;i++){if($i==user_seq)c1=i; if($i==trimmed_seq)c2=i; if ($i==original_seq)c3=i; if ($i==receptor_group)c4=i; if ($i==epitopes)c5=i; if ($i==source_organisms)c6=i; if ($i==source_antigens)c7=i;}} NR>1{print $c1, $c2, $c3, $c4, $c5, $c6, $c7}' $pairs_file > $pairs_subset_file) 2> $time_dir/fileprocessing_time.txt

# run TCRMatch on each line
(/usr/bin/time -f "exitcode %x\nuser     %U\nsystem   %S\nelapsed  %E\nmaxrss   %M" bash scripts/run_tcrmatch_loop.sh $tcrmatch_path $pairs_subset_file $tmp_dir $threshold $tcrmatch_outfile) 2> $time_dir/tcrmatch_time.txt


rm -r $tmp_dir

