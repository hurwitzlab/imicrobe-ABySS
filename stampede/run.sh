#!/bin/bash

module load singularity

echo "iMicrobe ABySS begin"
echo "run.sh arguments:"
echo "$@"

pwd
ls -l

singularity exec imicrobe-abyss.img python3.6 /scripts/agave_to_abyss_cmd_line_args.py $@

echo "iMicrobe ABySS completed"
