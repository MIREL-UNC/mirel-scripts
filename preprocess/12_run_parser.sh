#!/usr/bin/env bash

# Arguments:
# The directory where the input files (.conll) are.
# The output directory for the parsed files
# The output directory for the simplified files
# The directory to the maltparser

function maxjobs {
  while [ `jobs | wc -l` -ge 4 ]
  do
    sleep 5
  done
}

find $1 -type f -name "*.conll" -maxdepth 1| (while read file
do
  maxjobs
  filename=$(basename $file)
  echo "Analyzing $filename"
  java -Xmx3G -jar $4/maltparser-1.8.1/maltparser-1.8.1.jar -w $4/maltparser-1.8.1/models/ -c engmalt.linear-1.7 -m parse -i $file -o $2/$filename &> logs/${filename}.parser.log &
done
wait)

find $2 -type f -name "*.conll" | (while read file
do
  maxjobs
  filename=$(basename $file)
  echo "Simplyfing $filename"
  awk '{ print $1 "\t" $2 "\t" $4 "\t" $6 "\t" $7 "\t" $8 }' $file > $3/$filename &
done
wait)

echo "All jobs done"
