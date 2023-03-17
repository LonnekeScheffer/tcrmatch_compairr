#scripts_dir=/Users/lonneke/PycharmProjects/tcrmatch_compairr/scripts/file_processing_benchmark

scripts_dir=/storage/lonnekes/TCRMatch_CompAIRR/file_processing_benchmark
pairs_file=$scripts_dir/pairs.tsv

time_folder=$scripts_dir/out_time

mkdir $time_folder


for chunk_size in 1000 10000 100000 1000000 10000000
do

echo "chunking and df export chunksize $chunk_size"
/usr/bin/time -f "exitcode %x\nuser     %U\nsystem   %S\nelapsed  %E\nmaxrss   %M" python3 $scripts_dir/chunk_df_solution.py --pairs_file $pairs_file --output_folder $scripts_dir/out_pandas_chunk_df$chunk_size --chunk_size $chunk_size #) 2> $time_folder/time_pandas_k2.txt

done

echo "pandas original (no chunk) minus drop duplicates"
/usr/bin/time -f "exitcode %x\nuser     %U\nsystem   %S\nelapsed  %E\nmaxrss   %M" python3 $scripts_dir/orig_pandas_solution.py --pairs_file $pairs_file --output_folder $scripts_dir/out_pandas_orig #) 2> $time_folder/time_pandas1.txt
