#!/usr/bin/env bash

[ -n "$AUDREY_VAR_KATELLO_REGISTER_NOTIFY_EMAIL" ] && {
    cd results-dir
    touch result
    for f in *.log
    do
        echo "[$f]" >> result
        cat $f >> result
        echo "" >> result
    done
    cat result | mail -s "task finished on $HOSTNAME" "$AUDREY_VAR_KATELLO_REGISTER_NOTIFY_EMAIL"
    rm -f result
    cd ..
    }