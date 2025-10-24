# Lab Notebook

# File Storage

- vcf files for each cell line are located in `/projects/bgmp/shared/groups/2025/sarcoma/shared/250711_lewings_lines/pacbiowdlR/`

# Week 4

- We created a list of genes that, based on literature, may be associated w/ EwS:
 https://docs.google.com/spreadsheets/d/1eYBbficB6rVrvqe-5xCBs-dhWAPUE2pI4mQhDDZ0H7M/edit?gid=0#gid=0

### BED File Creation

- Created a .bed file from list of collected genes, containing chromosome and position information for each gene

> Rmd file: `GenerateBED.Rmd`
> 
- Installation of biomaRt:
    
    ```bash
    if (!require("BiocManager", quietly = TRUE))
        install.packages("BiocManager")
    
    BiocManager::install("biomaRt")
    ```
    
- Created BED file + changed names of chromosomes to match format observed in .vcf files:
    
    ```bash
    zcat A4573.GRCh38.structural_variants.phased.vcf.gz | grep -v "^#" | cut -f 1 | sort | uniq -c | sort -rn
    
    3948 chr2
    3890 chr1
    3118 chr7
    3062 chr6
    3032 chr5
    2928 chr3
    2761 chr4
    2484 chr12
    2457 chr11
    2427 chr8
    2101 chrX
    1978 chr9
    1884 chr10
    1762 chr17
    1721 chr13
    1554 chr14
    1522 chr18
    1495 chr16
    1493 chr15
    1426 chr20
    1259 chr19
    1107 chr22
    1101 chr21
    50 chr22_KI270737v1_random
    42 chrUn_KI270438v1
    32 chr2_KI270715v1_random
    27 chrUn_KI270442v1
    25 chrY
    25 chr22_KI270738v1_random
    23 chr16_KI270728v1_random
    21 chrUn_GL000224v1
    20 chr22_KI270736v1_random
    20 chr17_KI270729v1_random
    18 chr1_KI270712v1_random
    15 chr14_GL000225v1_random
    15 chr14_GL000009v2_random
    14 chr17_GL000205v2_random
    13 chrUn_KI270538v1
    13 chr22_KI270733v1_random
    13 chr17_KI270730v1_random
    12 chrUn_GL000219v1
    12 chrUn_GL000195v1
    12 chr14_GL000194v1_random
    11 chrUn_KI270467v1
    11 chr4_GL000008v2_random
    11 chr15_KI270727v1_random
    11 chr14_KI270725v1_random
    10 chr3_GL000221v1_random
    9 chrUn_GL000220v1
    9 chr1_KI270709v1_random
    8 chr9_KI270719v1_random
    8 chr22_KI270734v1_random
    7 chrUn_KI270466v1
    7 chr22_KI270731v1_random
    7 chr14_KI270723v1_random
    6 chr22_KI270732v1_random
    5 chr5_GL000208v1_random
    5 chr2_KI270716v1_random
    5 chr14_KI270724v1_random
    5 chr14_KI270722v1_random
    4 chrUn_KI270741v1
    4 chrUn_KI270589v1
    3 chrUn_KI270747v1
    3 chrUn_KI270435v1
    3 chrM
    3 chr1_KI270713v1_random
    2 chr9_KI270718v1_random
    2 chr22_KI270735v1_random
    2 chr1_KI270707v1_random
    1 chrUn_KI270751v1
    1 chrUn_KI270591v1
    1 chrUn_KI270588v1
    1 chrUn_KI270519v1
    1 chrUn_KI270518v1
    1 chrUn_KI270507v1
    1 chrUn_GL000214v1
    1 chr9_KI270720v1_random
    1 chr9_KI270717v1_random
    1 chr1_KI270711v1_random
    ```
    
- Removed all genes that fell on non-canonical chromosomes, because their names do not match non-canonical chromosomes in these .vcf files
- Final .bed file: `EwSAscGenes.bed`
    
    ```bash
    head EwSAscGenes.bed
    
    CDC20	chr1	43358928	43363207
    JAK1	chr1	64833223	65067754
    GNG5	chr1	84498284	84507237
    ID2	chr2	8678845	8684461
    MEIS1	chr2	66433452	66573898
    DYNC1I2	chr2	171687409	171750158
    FN1	chr2	215360440	215436120
    IGFBP5	chr2	216672105	216695549
    FEV	chr2	218981087	218985184
    CUL3	chr2	224470150	224585397
    ```
    

### Filtering vcf Files

- Created a test input file using data from `TC32.GRCh38.structural_variants.phased.vcf.gz`
    
    ```bash
    # adding headers
    zcat TC32.GRCh38.structural_variants.phased.vcf.gz | grep -"^#" > vcf_filtering_test_input.vcf
    
    # adding ~100 lines from thoughout the .vcf file so that test file contains variants from most chromosomes
    zcat TC32.GRCh38.structural_variants.phased.vcf.gz | grep -v "^#" | sed -n '1~600p' >> vcf_filtering_test_input.vcf
    
    ```
    
    - Modified test file so that some variants fall within genes in BED file