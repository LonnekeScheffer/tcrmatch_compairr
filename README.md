# CompAIRR + TCRMatch pipeline

A pipeline using CompAIRR as pre-filter for TCRMatch 

## Benchmarking

To repeat the benchmarking, the script [benchmark.sh](scripts/compare_pipelines_version/benchmark.sh) should be used. 
Internally, the script uses the [GNU time command](https://www.gnu.org/software/time/) (`/usr/bin/time`) 
to benchmark the time (user, system, elapsed) and memory (maxrss) usage. 
Several paths must be specified at the beginning of the benchmarking script:
- iedb_input: the path to the IEDB database ([IEDB_data.tsv](data/IEDB_data.tsv))
- compairr_iedb_input: path to an alternatively formatted IEDB database file, which uses column name 'cdr3_aa' instead of 'trimmed_seq' ([IEDB_for_compairr.tsv](data/IEDB_for_compairr.tsv))
- infiles_folder: folder where multiple user-input files are located. Their names must match the following pattern: n<number of sequences>_p<percentage iedb sequences>.tsv. For example: n1e3_p1.0.tsv. Each file must contain the 'cdr3_aa' header. ([infiles](data/benchmarking_data))
- output_folder: folder where benchmarking results will be stored. If this folder is already present, **it will be overwritten without warning**. 
- compairr_path: path to CompAIRR executable
- tcrmatch_path: path to TCRMatch executable
- compairr_tcrmatch_path: path to CompAIRR+TCRMatch python script

The current benchmarking pipeline is v6. The results for this pipeline are not done yet (will be added to the git repo once done).
The benchmarking script will create two output folders: one folder contains all TCRMatch output files,
the other folder contains the results of the GNU time command and CompAIRR log files.
The script [plot_benchmarking_results.py](other_scripts/plot_benchmarking_results.py) can subsequently 
be used to make plots of the time results. Note: for pipeline v6 it is not possible anymore to get the 'breakdown'
of compairr vs file processing vs TCRMatch running time, as everything is now called from a single python script. 

## Stand-alone script

The stand-alone CompAIRR+TCRMatch pipeline can be found in [tcrmatch_compairr_pipeline.py](scripts/tcrmatch_compairr_pipeline.py).
This script has a more developed user interface and provides checking of input parameter and user-friendly error messages.