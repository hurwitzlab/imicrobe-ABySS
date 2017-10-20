#!/bin/bash

echo "Started iMicrobe ABySS template.sh $(date)"

echo "NAME                    \"${NAME}\""
echo "KMER_LENGTH             \"${KMER_LENGTH}\""
echo "FORWARD_READS           \"${FORWARD_READS}\""
echo "REVERSE_READS           \"${REVERSE_READS}\""
echo "SINGLE_END_READS        \"${SINGLE_END_READS}\""
echo "FORWARD_MATE_PAIRS      \"${FORWARD_MATE_PAIRS}\""
echo "REVERSE_MATE_PAIRS      \"${REVERSE_MATE_PAIRS}\""
echo "LONG_SEQS               \"${LONG_SEQS}\""
echo "ADDITIONAL_ARGS         \"${ADDITIONAL_ARGS}\""

##mkdir abyss-out

time sh run.sh \
    ${NAME} ${KMER_LENGTH} ${FORWARD_READS} ${REVERSE_READS} ${SINGLE_END_READS} ${FORWARD_MATE_PAIRS} ${REVERSE_MATE_PAIRS} ${LONG_SEQS} ${ADDITIONAL_ARGS}

echo "Ended iMicrobe ABySS template.sh $(date)"
exit 0
