#!/bin/bash

#SBATCH -A iPlant-Collabs
#SBATCH -N 1
#SBATCH -n 16
#SBATCH -t 00:30:00
#SBATCH -p development
#SBATCH -J test-imicrobe-abyss
#SBATCH --mail-type BEGIN,END,FAIL
#SBATCH --mail-user jklynch@email.arizona.edu

module load irods

INPUT_DIR=test/input
if [[ -d $INPUT_DIR ]]; then
  rm -rf $INPUT_DIR
fi

mkdir -p $INPUT_DIR
iget -v test/imicrobe-abyss/fragScSi_1.fq $INPUT_DIR
iget -v test/imicrobe-abyss/fragScSi_2.fq $INPUT_DIR

OUTPUT_DIR=test/output
if [[ -d $OUTPUT_DIR ]]; then
  rm -rf $OUTPUT_DIR
fi

mkdir -p $OUTPUT_DIR

./run.sh --name $OUTPUT_DIR/test --kmer-length 64 -fp $INPUT_DIR/fragScSi_1.fq -rp $INPUT_DIR/fragScSi_2.fq
