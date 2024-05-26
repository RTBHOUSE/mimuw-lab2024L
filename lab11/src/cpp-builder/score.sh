#!/bin/bash

echo "${CODE}" > source.cpp
g++ -Wall -x c++ source.cpp

EXAMPLES_PATH="examples/${TASK_ID}"

find "${EXAMPLES_PATH}" -name '*.in' -exec basename -s .in {} \; | \
while read test; do
    echo "" > out
    ./a.out < "${EXAMPLES_PATH}/${test}.in" > out
    echo -n "$? "

    diff out "${EXAMPLES_PATH}/${test}.out" > /dev/null
    echo "$?"
done

