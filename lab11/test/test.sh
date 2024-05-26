#!/bin/bash

DIR=$(dirname $0)

curl -v -X POST -H 'content-type: text/plain' -d @"${DIR}/test_source.cpp" http://localhost:5000/tasks/sort/score
