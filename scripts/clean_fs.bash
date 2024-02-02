#!/bin/bash

# delete manuals
rm public/airlines_files/manuals/*.pdf

# delete attachments
shopt -s extglob
rm public/airlines_files/attachments/!(*.txt)
