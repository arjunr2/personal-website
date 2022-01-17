#!/bin/bash

REMOTE_DIR=/afs/ece.cmu.edu/usr/arjunr2/public_html
BASE_DIR=$(dirname "$0")

# Push updates and deploy gh-pages
set -x
git -C $BASE_DIR push
set +x 

if [ $? -ne 0 ]; then
  echo "Failed script"
  exit 1
fi

sleep 1

# Update CMU website (rebase needed for forced gh-page push)
set -x
ssh afs "git -C $REMOTE_DIR pull --rebase"
set +x

if [ $? -ne 0 ]; then
  echo "Failed script"
  exit 1
fi

echo "Completed deployment successfully!"
