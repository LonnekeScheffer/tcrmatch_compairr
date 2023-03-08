# CompAIRR + TCRMatch pipeline

A pipeline using CompAIRR as pre-filter for TCRMatch 

## Benchmarking

To repeat the benchmarking, the script [benchmark.sh](scripts/compare_pipelines_version/benchmark.sh) should be used. 
Internally, the script uses the [GNU time command](https://www.gnu.org/software/time/) (`/usr/bin/time`) 
to benchmark the time (user, system, elapsed) and memory (maxrss) usage. 
Several paths must be specified at the beginning of the benchmarking script:
- iedb_input: the path to the IEDB database ([IEDB_data.tsv](data/IEDB_data.tsv))
- compairr_iedb_input: TEMPORARY SOLUTION path to an alternatively formatted IEDB database file ([IEDB_for_compairr.tsv](data/IEDB_for_compairr.tsv))
- infiles_folder: folder where multiple user-input files are located. Their names must match the following pattern: n<number of sequences>_p<percentage iedb sequences>.tsv. For example: n1e3_p1.0.tsv. Each file must contain the 'cdr3_aa' header. ([infiles](data/benchmarking_data))
- output_folder: folder where benchmarking results will be stored. If this folder is already present, **it will be overwritten without warning**. 
- compairr_path: path to CompAIRR executable
- tcrmatch_path: path to TCRMatch executable

The current benchmarking pipeline is v3. The newest benchmarking results are not done yet (will be updated once done).
Example benchmarking results for pipeline v2 are available in the folder [benchmarking_v2](benchmarking_v2). 

The benchmarking script will create two output folders: one folder contains all TCRMatch output files ([tcrmatch_outfiles](benchmarking_v2/tcrmatch_outfiles)),
the other folder contains the results of the GNU time command and CompAIRR log files ([time](benchmarking_v2/time)). 
The script [plot_benchmarking_results.py](other_scripts/plot_benchmarking_results.py) can subsequently
be used to make plots of the time results. 