## localization
cd ../collections

## pandoc convert HTML to markdown
ls *html | awk -F'.html' '{print "pandoc "$0" -f html -t markdown -s -o ../preprocess/"$1".md"}' | sh

## python postprocess
cd ../scripts
python3 rename_and_listed.py article_list.txt ../preprocess/ ../prepared/
