#!/bin/bash

pip install black fiximports

for file in ./app/*
do
    if [[ -f $file ]]; then
        fiximports $file
    fi
done
for file in ./tests/*
do
    if [[ -f $file ]]; then
        fiximports $file
    fi
done

black --exclude ".*|.venv|.vscode|migrations" .
tox