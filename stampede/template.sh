#!/bin/bash

echo "Started $(date)"

echo "SINGLE_END_READS        \"${SINGLE_END_READS}\""
echo "FORWARD_READS           \"${FORWARD_READS}\""
echo "REVERSE_READS           \"${REVERSE_READS}\""
echo "NAME                    \"${NAME}\""
echo "k                       \"${k}\""
echo "ADDITIONAL_ARGS         \"${ADDITIONAL_ARGS}\""

mkdir abyss-out

sh run.sh \
    ${NAME} \
    ${k} \
    ${FORWARD_READS} ${REVERSE_READS} ${SINGLE_END_READS}

echo "Ended $(date)"
exit 0
