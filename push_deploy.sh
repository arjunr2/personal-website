#!/bin/bash

REMOTE_DIR=/afs/ece.cmu.edu/usr/arjunr2/public_html
BASE_DIR=$(dirname "$0")

# Push updates and deploy gh-pages
git -C $BASE_DIR push
sleep 5

# Update CMU website (rebase needed for forced gh-page push)
ssh afs 'git -C pull $REMOTE_DIR --rebase'

echo "Completed deployment!"
