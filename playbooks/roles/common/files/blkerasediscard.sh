#!/usr/bin/env bash

set -eu -o pipefail

if [ "$#" -ne 1 ]; then
	cat <<-ENDOFMESSAGE
Usage: $0 DEVICE

Secure erase and discard all the sectors on the drive.

Note that this script is EXCEPTIONALLY DANGEROUS.
See the option --trim-sector-ranges of hdparm.

For secure erase operation, see
https://www.thomas-krenn.com/en/wiki/SSD_Secure_Erase
https://storage.toshiba.com/docs/services-support-documents/ssd_application_note.pdf
ENDOFMESSAGE
	exit
fi

if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root!"
    exit 1
fi

device="$1"
if [ ! -b "$device" ]; then
	echo "$device is not a block device"
    exit 2
fi

echo "start secure erasing device $device ..."

if ! hdparm -I "$device" | grep "not\\s*frozen" &> /dev/null || \
   ! hdparm -I "$device" | grep "supported:\\s*enhanced erase" &> /dev/null ; then
    printf "device %s is frozen or does not support enhanced erase.
Please check the output of hdparm -I %s\\n" "$device" "$device"
    exit 3
fi

hdparm --user-master u --security-set-pass NULL "$device" > /dev/null
hdparm --user-master u --security-erase NULL "$device" > /dev/null

if hdparm -I "$device" | grep "not\\s*enabled" &> /dev/null ; then
    echo "successfully secure erased device $device"
else
    printf "failed to disable the security feature.
Please check the output of hdparm -I %s\\n" "$device"
    exit 3
fi


printf "\\nstart trimming device %s ...\\n" "$device"

total_sectors="$(blockdev --getsz "$device")"
echo "total 512-byte $total_sectors on device $device"

MAXSECT=65535

sectors="$total_sectors"
pos=0

while [ "$sectors" -gt 0 ]; do
    if [ "$sectors" -gt "$MAXSECT" ]; then
	    size="$MAXSECT"
    else
        size="$sectors"
    fi

    hdparm --please-destroy-my-drive --trim-sector-ranges "$pos":"$size" "$device" > /dev/null

	sectors=$(( sectors - size ))
	pos=$(( pos + size ))
done

echo "successfully trimmed all $total_sectors"

printf "\\ndone!\\n"
