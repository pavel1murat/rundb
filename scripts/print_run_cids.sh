#!/usr/bin/sh
#------------------------------------------------------------------------------
# example:  . rundb/scripts/print_run_cids.sh KPP_reco v1_2 125470
#------------------------------------------------------------------------------
purpose=$1
version=$2
run_number=$3

table_names=`dbTool print-table --purpose $purpose --version $version | grep -v TID | awk '{print $2}'`

for table in $table_names ; do
    dbTool print-run  --run $run_number --table $table --purpose $purpose --version $version | grep $table
done
