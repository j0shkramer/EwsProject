# EwS Lab Notebook

# Project Goal

- Explore relationships between chromatin structure, cis-regulatory element usage, and transcriptional states in Ewing Sarcoma (EwS) to better understand heterogeneity

# Set Up & File Storage

## GitHub

[https://github.com/j0shkramer/EwsProject](https://github.com/j0shkramer/EwsProject)

- cloned on my laptop at `~/bioinfo/EwS_Project/EwsProject`
- cloned on Talapas at `/projects/bgmp/shared/groups/2025/sarcoma/vini/EwsProject`

## My Computer

- project directory is `~/bioinfo/EwS_Project`

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
    - was emailed a download link, from which I downloaded `annovar.latest.tar.gz`
    - transferred `tar.gz` file to Talapas using `scp` + extracted it using `tar -xvzf`
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
    4. aggregated all ANNOVAR output `.txt` files (from each cell line) into a single file, `all_cell_lines_annovar_output.txt`
    - this script was run on an interactive node and took a few minutes to run
        - ANNOVAR gave a few warnings about some invalid alternative/reference alleles, but nothing concerning
        - resulting file was 479761 lines (1 for every structural variant annotated + header line)
- wrote a Python script (`extract_sv_info.py`) that parsed through `annovar_all_cell_lines_output.txt` + output a table (`ews_sv_genes.txt`) w/ the following format:
    
    
    | gene_type | gene | cell_line | sv_type | sv_len |
    | --- | --- | --- | --- | --- |
    |  |  |  |  |  |
    - the script has an option to split intergenic variants into 2 lines (one each for the upstream + downstream gene): `-i` flag
        - if this flag is not specified, the gene name for intergenic variants will be the 2 genes separated by a “|”
    - script ran within a minute:
        
        ```bash
        ./extract_sv_info.py -a all_cell_lines_annovar_output.txt -o ews_sv_genes.txt
        ```
        
        ```bash
        ./extract_sv_info.py -a all_cell_lines_annovar_output.txt -i -o ews_sv_genes_intergenic_split.txt
        ```
        
    - gene_type:
        
        ```bash
        cat ews_sv_genes.txt | cut -d ',' -f  1| sort | uniq -c
        ```
        
        | gene type | frequency | notes |
        | --- | --- | --- |
        | intergenic | 212282 |  |
        | intronic | 167236 |  |
        | ncRNA_intronic | 78087 |  |
        | upstream | 5213 | close to gene |
        | ncRNA_exonic | 5190 |  |
        | downstream | 5087 | close to gene |
        | exonic | 2547 |  |
        | UTR3 | 2831 |  |
        | UTR5 | 830 |  |
        | upstream;downstream | 318 |  |
        | splicing | 86 |  |
        | ncRNA_splicing | 37 |  |
        | exonic;splicing | 9 |  |
        | ncRNA_UTR5 | 6 |  |
        | UTR5;UTR3 | 1 |  |
    - sv_type:
        
        ```bash
        cat ews_sv_genes.txt | cut -d ',' -f 4 | sort | uniq -c
        ```
        
        | structural variant type | frequency |
        | --- | --- |
        | DEL | 218336 |
        | INS | 235002 |
        | DUP | 25447 |
        | INV | 975 |

# Structural Variant Transcriptional Effects

- identifying whether or not each structural variant gene is differentially expressed between cell lines that have structural variant(s) in that gene vs. cell lines that do not
- working w/ integrated + annotated Seurat object in R: `seurat_integration_finalAnnotations.rds`
- wrote a Python script (`extract_sv_gene_cl_combos.py`) that took  `ews_sv_genes.txt` + created a table that has the following format:
    
    
    | CellLineCombo | Gene |
    | --- | --- |
    | A4573-A673-CHLA10-CHLA9-RDES-SKNMC-TC32-TC71 | GP1BB |
    | A4573-PDX305-SKNMC | S100A9 |
    | A4573 | IFFO1 |
    | A4573-A673-CHLA10-CHLA9 | WDR97|HGH1 |
    - script took ~10 minutes to run:
        
        ```bash
        ./extract_sv_gene_cl_combos.py -i ews_sv_genes.txt -o sv_gene_cl_combos.csv
        ```
        
- R Markdown testing differential expression of SV-associated genes on my computer in project directory: `SingleCell/scRNA_9cl_Differential_Expression.Rmd`
    - used MAST for differential expression (DE) (built for scRNA-seq whereas DESeq2 is meant for bulk RNA-seq)
        
        ```
        BiocManager::install("MAST")
        ```
        
    - only looked at top 40 cell line combinations (that had the most number of genes) for purpose of visualizaion
        - for each cell line combination:
            - ran `FindAllMarkers()` for SV-associated genes that were in each cell line in that cell line combination and not in the other cell lines
            - counted how many SV-associated genes were DE (adjusted p < 0.05, |log2FC| > 1)
                - if SV was intergenic:
                    - it counted as differentially expressed if either one of the genes flanking it was differentially expressed
        - output a table (`sv_differential_expression_stats.csv`) w/ the following format:
            
            
            | CellLineCombo | unique_sv_genes | intergenic_sv_genes | intragenic_sv_genes | de_intergenic_sv_genes | de_intragenic_sv_genes |
            | --- | --- | --- | --- | --- | --- |
            | A673-CHLA10-CHLA9-TC32 | 87 | 38 | 49 | 3 | 3 |
            | A4573-A673-CHLA10-CHLA9-PDX305-RDES-SKNMC-TC32 | 372 | 167 | 205 | 32 | 39 |
            - overall, a relatively small proportion of SV-associated genes were found to be DE
            - created an UpSet plot w/ stacked bars for poster, w/ each bar showing proportion of SVs that were DE
                - could not find a plotting tool/package that would do this, hence had to do it from scratch

## CHLA9 vs. CHLA10

- 1146 structural variant genes from CHLA cell lines were found in Seurat object
    - all 1146 were associated with structural variants in CHLA10
    - 1118 were associated with structural variants in CHLA9
    - 28 (1146 - 1118) unique to CHLA10
        - 17/28 (60.7%) were differentially expressed between CHLA9 & 10
            - Average absolute log2FC: 1.07
            - Median absolute log2FC: 0.45
    - 642/1118 (58.3%) of genes associated w/ structural variants in both cell lines were differentially expressed between CHLA9 & CHLA10
        - Average absolute log2FC: 0.72
        - Median absolute log2FC: 0.44
    - rate of DE of genes in both cell lines vs. genes in just CHLA10 is approximately same, supporting the conclusion that SVs are not driving transcriptional differences

# Motif Enrichment (CHLA9 vs. CHLA10)

- **motif**: short, recurring pattern of nucleotides that has biological meaning
    - often involved in regulation of gene expression

## HOMER

- **HOMER**: Hypergeometric Optimization of Motif EnRichment
    - identifies enriched motifs (both canonical + de novo)
    - compares enriched motifs to known motifs
    - identifies candidate transcription factors that likely bind to them

### Installation & Set-Up

- installation instructions: [http://homer.ucsd.edu/homer/introduction/install.html](http://homer.ucsd.edu/homer/introduction/install.html)
- downloaded [configureHomer.pl](http://configureHomer.pl) + transferred to talapas
- installation:
    
    ```bash
    perl configureHomer.pl -install homer
    ```
    
- installing human genome (hg38):
    
    ```bash
    perl configureHomer.pl -install hg38
    ```
    

### Running HOMER

- CHLA9 run:
    - foreground peaks: CHLA9 DA (differentially accessible) peaks (`atac_peaks_chla9_da.bed`)
    - background peaks: all CHLA9 + CHLA10 peaks (`atac_peaks.bed`)
    
    ```bash
    perl findMotifsGenome.pl atac_peaks_chla9.bed hg38 -bg atac_peaks.bed homer_output_chla9/
    ```
    
- CHLA10 run:
    - foreground peaks: CHLA10 DA peaks (`atac_peaks_chla9_da.bed`)
    - background peaks: all CHLA9 + CHLA10 peaks (`atac_peaks.bed`)
    
    ```bash
    perl findMotifsGenome.pl atac_peaks_chla9.bed hg38 -bg atac_peaks.bed homer_output_chla9/
    ```
    

### Interpreting Results

- output of HOMER:
    - de novo motif finding:
        
        ```bash
        # separate runs of algorithm, with number indicating k-mer size?
        homerMotifs.motifs10
        homerMotifs.motifs12
        homerMotifs.motifs8
        
        homerMotifs.all.motifs # all motifs combined in 1
        homerResults/
        homerResults.html # report
        ```
        
    - canonical motif finding (of interest to us):
        
        ```bash
        knownResults/
        knownResults.html # report
        knownResults.txt # statistics
        ```
        
    - `motifFindingParameters.txt`: command used to execute script
    - `seq.autonorm.tsv`: autonormalization statistics
    - copied each run’s output to `SingleCell/` directory in project directory on my computer:
        
        ```bash
        homer_output_chla9/
        homer_output_chla10/
        ```
        
- from `knownResults.html` files, identified recurrent transcription factor (TF) families enriched in each cell line:
    
    
    | CHLA9 | CHLA10 |
    | --- | --- |
    | HOX/Homeobox | RFX/HTH
    RUNX |

## ChromVAR Deviation Scores

- measure of bias corrected (normalized for GC bias + sequencing depth) chromatin accessibility
- higher score means more accessible
- calculated from scATAC-seq data
- R Markdown notebook on my computer in project directory: `SingleCell/scATAC_CHLA9_vs_CHLA10_ChromVAR.Rm`
    - installation of packages:
        
        ```bash
        BiocManager::install("chromVAR")
        devtools::install_version("TFMPvalue", version = "0.0.9")
        BiocManager::install("JASPAR2020")
        BiocManager::install("motifmatchr")
        BiocManager::install("ComplexHeatmap")
        ```
        
    - calculated chromVAR deviation scores for TF families identified via HOMER in CHLA9 + CHLA10 cell lines
    - created heatmap w/ scores for top 5 motifs per TF family, which validated that these TF families are differentially accessible between CHLA9 + CHLA10
        - identified an additional family that is differentially accessible: AP-1 (includes Fos and Jun TFs)
        - recreated this heatmap more cleanly in poster