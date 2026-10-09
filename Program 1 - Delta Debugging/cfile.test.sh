#!/bin/bash
if gcc -o a.out -x c $1 &> cmp_out; then
    if ./a.out &> run_out; then
        if grep "correct" run_out; then
            rm -f ./a.out run_out cmp_out
            echo "0"                 # interesting
            exit 0;
        fi
    fi
fi
rm -f ./a.out run_out cmp_out
echo "1"                         # not interesting
exit 1;
