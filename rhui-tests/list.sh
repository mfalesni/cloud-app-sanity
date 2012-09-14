#!/usr/bin/env bash

[ ! -e "${1}" ] && exit 1

cat "${1}" | sed -r -e "s/^#.*$//" | sed "/^$/d" | sort

