# Script to process a (unparsed) conll document for the ner-annotation tool
# The expected input format is:
# number \t token \t pos tag \t label

# Usage:
# bash 21_process_for_annotation.sh input_dirpath output_dirpath

for filename in `ls $1`; do
    if [[ $filename =~ .*.conll$ ]];then
        awk '{if ($1=="") {print ""} }{if (match($1, /[0-9]+/)) {print $4 "\t0\t" $1 "\tx\t" $3 "\t" $2 "\tx\tx\t0"}}' "$1/$filename" > "$2/$filename"
    fi
done
