#!/bin/bash

module load singularity

echo "$@"

#ABYSS_CMD_LINE_ARGS=`singularity exec imicrobe-abyss.img python3 /scripts/agave_to_abyss_cmd_line_args.py $@`

#echo "ABySS command line args: \"${ABYSS_CMD_LINE_ARGS}\""

#singularity run imicrobe-abyss.img ${ABYSS_CMD_LINE_ARGS}
