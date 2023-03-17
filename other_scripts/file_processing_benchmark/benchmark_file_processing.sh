#scripts_dir=/Users/lonneke/PycharmProjects/tcrmatch_compairr/scripts/file_processing_benchmark

scripts_dir=/storage/lonnekes/TCRMatch_CompAIRR/file_processing_benchmark
pairs_file=$scripts_dir/pairs.tsv

time_folder=$scripts_dir/out_time

mkdir $time_folder

chunk_size=100000

echo "chunking and df export"
/usr/bin/time -f "exitcode %x\nuser     %U\nsystem   %S\nelapsed  %E\nmaxrss   %M" python3 $scripts_dir/chunk_df_solution.py --pairs_file $pairs_file --output_folder $scripts_dir/out_pandas_chunk_df --chunk_size $chunk_size #) 2> $time_folder/time_pandas_k2.txt

echo "stringio"
/usr/bin/time -f "exitcode %x\nuser     %U\nsystem   %S\nelapsed  %E\nmaxrss   %M" python3 $scripts_dir/stringio_solution.py --pairs_file $pairs_file --output_folder $scripts_dir/out_pandas_stringio --chunk_size $chunk_size #) 2> $time_folder/time_pandas_k2.txt

echo "chunking and writing after"
/usr/bin/time -f "exitcode %x\nuser     %U\nsystem   %S\nelapsed  %E\nmaxrss   %M" python3 $scripts_dir/chunk_write_solution.py --pairs_file $pairs_file --output_folder $scripts_dir/out_pandas_chunk_write --chunk_size $chunk_size #) 2> $time_folder/time_pandas_k3.txt

echo "pandas original (no chunk) minus drop duplicates"
/usr/bin/time -f "exitcode %x\nuser     %U\nsystem   %S\nelapsed  %E\nmaxrss   %M" python3 $scripts_dir/orig_pandas_solution.py --pairs_file $pairs_file --output_folder $scripts_dir/out_pandas_orig #) 2> $time_folder/time_pandas1.txt

echo "awk"
/usr/bin/time -f "exitcode %x\nuser     %U\nsystem   %S\nelapsed  %E\nmaxrss   %M" bash $scripts_dir/awk_solution.sh $pairs_file $scripts_dir/out_awk_dir1 $scripts_dir/out_awk_dir2 #) 2> $time_folder/time_bash.txt


