# Selects random wikipedia documents from the docs_for_ner.txt file
# Expects that each document is stored in a single line.
# Clean all html content of the document, leaving only raw text.
#
# Arguments:
#   The full path to the docs_for_ner.txt file (or equivalent)
#   The number of documents to extract
#   The output file

input_file=$1
n_files=$2
output_file=$3

shuf -n $n_files $input_file > $output_file

# Clean html tags
sed -i -e 's/<[^>]*>//g' $output_file
echo "Extraction completed. Word counts:"
wc $output_file
