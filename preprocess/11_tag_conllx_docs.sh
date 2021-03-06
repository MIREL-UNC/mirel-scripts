#!/usr/bin/env bash

# Arguments:
# The directory where the input files (.conll) are.
# The output directory

function maxjobs {
  while [ `jobs | wc -l` -ge 5 ]
  do
    sleep 5
  done
}

find $1 -type f -name "*.conll" | (while read file
do
  maxjobs
  filename=$(basename $file)
  echo "Analyzing $filename"
  total_lines=$(wc -l < "$file")
  output_file=$2/$filename
  ./10_tag_conllx_docs.py $file $output_file $total_lines &> logs/${filename}.log &
done
wait)
