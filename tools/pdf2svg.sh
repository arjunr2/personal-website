#!/bin/bash

cd "$(dirname "$0")/../static/assets/pubs"
for file in pdfs/*.pdf; do
  bn=$(basename $file .pdf)
#convert $file $bn.png
  inkscape --without-gui --file=$file --export-plain-svg=$bn.svg
done
