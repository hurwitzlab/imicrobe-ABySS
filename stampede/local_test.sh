#!/bin/bash -x


singularity exec imicrobe-abyss.img python3.6 ../scripts/agave_to_abyss_cmd_line_args.py $@
