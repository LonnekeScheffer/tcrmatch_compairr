tcrmatch_path=$1
threads=$2
threshold=$3
tmp_folder=$4
out_folder=$5


i=1
while [ -f $tmp_folder/user_cdr3_$i.txt ] && [ -f $tmp_folder/prefiltered_IEDB_$i.tsv ]
do
  single_cdr3_infile=$tmp_folder/user_cdr3_$i.txt
  iedb_prefiltered=$tmp_folder/prefiltered_IEDB_$i.tsv
  outfile=$out_folder/tcrmatch_result_$i.tsv
  $tcrmatch_path -i $single_cdr3_infile -a -t $threads -d $iedb_prefiltered -s $threshold > $outfile
  i=$(( $i + 1 ))
done