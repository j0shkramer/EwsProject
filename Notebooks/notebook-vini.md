# Lab Notebook

# Project Goal

- Explore relationships between chromatin structure, cis-regulatory element usage, and transcriptional states in EwS to better understand heterogeneity

# Set Up & File Storage

## GitHub

[https://github.com/j0shkramer/EwsProject](https://github.com/j0shkramer/EwsProject)

- cloned on my laptop at `~/bioinfo/Bi624/EwS_Project/EwsProject`
- cloned on Talapas at `/projects/bgmp/shared/groups/2025/sarcoma/vini/EwsProject`

## My Computer

- project directory is `~/bioinfo/Bi624/EwS_Project`

## Talapas

- group project directory is `/projects/bgmp/shared/groups/2025/sarcoma/`
- structural variant (`.vcf`) files for each cell line are located at: `/projects/bgmp/shared/groups/2025/sarcoma/shared/250711_lewings_lines/pacbiowdlR/`
- conda environment: ews_project
    - python version: 3.14.0
    - installed packages:
        - pandas: 2.3.3
        - numpy: 2.3.5
        - more-itertools: 10.8.8

### Accessing RStudio

- this was set up by running `run_rstudio_prod-v04.sh` w/ `sbatch`
    - script located at `/projects/bgmp/shared/groups/2025/sarcoma/vini`
    - will have to run again every 30 days
    - slurm log files located at `/projects/bgmp/shared/groups/2025/sarcoma/vini/rstudio_runs`
1. run this command on local machine:
    
    ```bash
    ssh -L 49615:localhost:48913 vini@login3.talapas.uoregon.edu -t ssh -L 48913:localhost:49615 n0350.talapas.uoregon.edu
    ```
    
2. log in w/ UO credentials
3. open web browser to:
    
    [http://localhost:49615/](http://localhost:49615/)
    
4. log in credentials:
    - username: vini
    - password: changeme123

# Structural Variant Annotation

- all files for this section are located on Talapas at `/projects/bgmp/shared/groups/2025/sarcoma/vini/variant_annotation`

## Selection of Annotation Tool

- researched options for adding gene names (annotation) to each variant in vcf files: bcftools and ANNOVAR
    - ANNOVAR was selected because
        - it comes with pre-built reference databases
        - it has more detailed output
        - seems pretty popular (paper has 15000+ citations)
            
            [ANNOVAR: functional annotation of genetic variants from high-throughput sequencing data](https://pmc.ncbi.nlm.nih.gov/articles/PMC2938201/)
            

### Installation & Set-Up

- installation of ANNOVAR:
    
    [Quick Start-Up Guide - ANNOVAR Documentation](https://annovar.openbioinformatics.org/en/latest/user-guide/startup/#download-and-install)
    
    - had to enter name, institution, and email to download
    - was emailed a download link, from which I downloaded annovar.latest.tar.gz
    - transferred tar.gz file to Talapas using scp + extracted it using tar -xvzf
- downloading most recent version of hg38 human genome (not sure if this was necessary but did it anyway):
    
    [Download ANNOVAR - ANNOVAR Documentation](https://annovar.openbioinformatics.org/en/latest/user-guide/download/#additional-databases)
    
    ```bash
    perl annotate_variation.pl -buildver hg38 -downdb -webfrom annovar ensGene41 humandb/
    ```
    

## Annotating Structural Variants

- preparing files for ANNOVAR:
    - ANNOVAR cannot deal w/ fusion variants, hence these were removed from vcf files using `grep -v "BND"`
- running ANNOVAR:
    
    ```bash
    perl annovar/table_annovar.pl <input_vcf.gz> annovar/humandb/ -buildver hg38 -out output/<output_prefix> -remove -protocol ensGene -operation g -nastring . -vcfinput -polish
    ```
    
    - annotated variants w/ Ensembl (not NCBI) gene names, as that is the format used within sc Seurat object
- ANNOVAR output: 3 files
    
    ```bash
    <output_prefix>.avinput
    <output_prefix>.hg38_multianno.txt
    <output_prefix>.hg38_multianno.vcf
    ```
    
    - the `multianno.txt` file is most useful for us
- wrote a bash script titled `run_annovar.sh` to loop through each cell line’s  `structural_variants.phased.vcf.gz` file and:
    1. remove fusion variants
    2. run ANNOVAR
    3. add cell line name as a new column
    4. aggregated all ANNOVAR output .txt files (from each cell ine) into a single file, `all_cell_lines_annovar_output.txt`
    - this script was run on an interactive node and took a few minutes to run
        - ANNOVAR gave a few warnings about some invalid alternative/reference alleles, but nothing concerning
        - resulting file was 479761 lines (1 for every structural variant annotated + header line)
- wrote a Python script (`extract_sv_info.py`) that parsed through `annovar_all_cell_lines_output.txt` + output a table (`ews_sv_genes.txt`) w/ the following format:
    
    
    | gene | gene_type | cell_line | sv_type | sv_len |
    | --- | --- | --- | --- | --- |
    |  |  |  |  |  |
    - script ran within a minute:
        
        ```bash
        ./extract_sv_info.py -a all_cell_lines_annovar_output.txt -o ews_sv_genes.txt
        ```
        
    - gene_type:
        
        ```bash
        cat ews_sv_genes.txt | cut -d ',' -f 3 | sort | uniq -c
        ```
        
        | gene type | frequency | notes |
        | --- | --- | --- |
        | intergenic | 406341 |  |
        | intronic | 173884 |  |
        | ncRNA_intronic | 84416 |  |
        | upstream | 5610 | close to gene |
        | ncRNA_exonic | 5369 |  |
        | downstream | 5286 | close to gene |
        | exonic | 3413 |  |
        | UTR3 | 2899 |  |
        | UTR5 | 835 |  |
        | upstream;downstream | 395 |  |
        | splicing | 86 |  |
        | ncRNA_splicing | 37 |  |
        | exonic;splicing | 9 |  |
        | ncRNA_UTR5 | 6 |  |
        | UTR5;UTR3 | 1 |  |
    - sv_type:
        
        ```bash
        cat ews_sv_genes.txt | cut -d ',' -f 5 | sort | uniq -c
        ```
        
        | structural variant type | frequency |
        | --- | --- |
        | DEL | 312952 |
        | INS | 337979 |
        | DUP | 36090 |
        | INV | 1566 |

# Structural Variant Transcriptional Effects

- working w/ integrated Seurat object in R
    - but used original RNA assay, as DESeq2 should be run on raw counts
- made summed (pseudo-bulk) counts for each cell line
- ran DESeq2 for each cell line vs. the others
- made list of structural variant genes unique to each cell line
- determined percent of unique structural variants that are in differentially expressed genes list

Next Steps:

- filter for SVs that are longer than a certain threshold
- KEGG & GO w/ genes
    - GO is more comprehensive
- module expression in Seurat