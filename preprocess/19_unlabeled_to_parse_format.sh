#!/usr/bin/env bash

# Script to convert a unlabeled document with PoS tags to the format expected
# by script 12_run_parser.sh
#
# The input file is expected to have the following tab-separated columns
#    index \t word_token \t POS tag \t label
# The output file will have the format:
#    index \t word_token \t _ \t POS tag \t POS tag \t label
#
# The first argument of the script is the input directory, the second is the
# output directory.

function maxjobs {
  while [ `jobs | wc -l` -ge 4 ]
  do
    sleep 5
  done
}

find $1 -type f -name "*.conll" | (while read file
do
  maxjobs
  filename=$(basename $file)
  echo "Processing $filename"
  awk '$1 ~ /[0-9]+/ {print $1 "\t" $2 "\t_\t" $3 "\t" $3 "\t" $4} $1 == "" {print ""}' $file > $2/$filename &
done
wait)


