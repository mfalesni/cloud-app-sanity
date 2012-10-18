#!/usr/bin/env bash

RESULTS_DIR="results"
if [ ! -d "$RESULTS_DIR" ]; then
    echo "Skipping.  Missing results directory: $RESULTS_DIR"
    exit 1
fi

case "$AUDREY_VAR_KATELLO_REGISTER_NOTIFY_EMAIL" in
    *@*)
        body=$(mktemp "$RESULTS_DIR/mail.XXXXXX")
        for f in "$RESULTS_DIR"/*.log
        do
            echo "[$f]" >> "$body"
            cat $f >> "$body"
            echo "" >> "$body"
        done
        cat "$body" | mail -s "Task finished on $HOSTNAME" "$AUDREY_VAR_KATELLO_REGISTER_NOTIFY_EMAIL"
        rm -f "$body"
        ;;
    *)
        echo "Skipping.  No valid email provided ('$AUDREY_VAR_KATELLO_REGISTER_NOTIFY_EMAIL')"
        echo 1
        ;;
esac
