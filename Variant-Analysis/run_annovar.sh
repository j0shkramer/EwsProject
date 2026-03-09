#!/bin/bash

cell_lines=("A673" "A4573" "CHLA9" "CHLA10" "PDX305" "RDES" "SKNMC" "TC32" "TC71")

touch "all_cell_lines_annovar_output.txt"

for cl in "${cell_lines[@]}"; do
    # remove fusion variants and copy resulting file over
    zcat "/projects/bgmp/shared/groups/2025/sarcoma/shared/250711_lewings_lines/pacbiowdlR/${cl}/${cl}.GRCh38.structural_variants.phased.vcf.gz" | grep -v "BND" | gzip > "input_vcf/${cl}.GRCh38.structural_variants_no_BND.phased.vcf.gz"

    # run annovar
    perl annovar/table_annovar.pl "input_vcf/${cl}.GRCh38.structural_variants_no_BND.phased.vcf.gz" annovar/humandb/ -buildver hg38 -out "output/${cl}_annovar_output" -remove -protocol ensGene -operation g -nastring . -vcfinput -polish -remove

    # add cell line name as a column to output file
    sed -i "s/$/\t${cl}/" "output/${cl}_annovar_output.hg38_multianno.txt"

    # delete input file
    rm -f "input_vcf/${cl}.GRCh38.structural_variants_no_BND.phased.vcf.gz"

    # delete output files that are not needed
    rm -f output/*avinput
    rm -f output/*vcf

    # add output contents to aggregated output file (excluding header line)
    cat "output/${cl}_annovar_output.hg38_multianno.txt" | tail -n +2 >> "all_cell_lines_annovar_output.txt"

done

# adding a single header line to top of aggregated output file
header=$(head -1 output/A673_annovar_output.hg38_multianno.txt | awk -v FS='\t' -v OFS='\t' 'NF{NF--};1')
header+=$'\t'
header+="CellLine"
sed -i "1i ${header}" "all_cell_lines_annovar_output.txt"
