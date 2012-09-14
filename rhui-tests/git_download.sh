#!/usr/bin/env bash

FILENAME="$1"
URL="$2"
TRIAL=1
MAXTRIAL=10
rpm -q wget > /dev/null || yum install -y wget
until [ $TRIAL -gt $MAXTRIAL ] ; do
	echo "Trial $TRIAL: Downloading \"${FILENAME}\", from ${URL}"
	wget -O "${FILENAME}" --no-check-certificate "${URL}" 2> /dev/null
	CONTAINS_HTML=$(grep -q '<!DOCTYPE html' $FILENAME ; echo $?)
	if [ -n "$(sed '/^[[:space:]]*$/d' $FILENAME)" ] && [ ! $CONTAINS_HTML -eq 0 ]; then
		echo "Download of $FILENAME successful"
		break;
	fi
	if [ $TRIAL -eq $MAXTRIAL ]; then
		echo "File corrupted and maximum number of trials reached. Removing $FILENAME and giving up."
	else
		echo "File corrupted. Removing $FILENAME and trying to download again."
	fi
	rm -f $FILENAME
	(( TRIAL++ ))
done

[ -f $FILENAME ] && exit 0 || exit 1
