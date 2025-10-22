# Saturday, October 18th

/projects/bgmp/shared/groups/2025/sarcoma

## Exploratory Data Analysis

Cell lines are stored in /shared
- A673, A4573, CHLA9, CHLA10, PDX305, RDES, SKNMC, TC32, TC71

### FiberTools
https://fiberseq.github.io/fire/outputs.html 

FIRE: Mtase sensitive patches (MSPs) that are inferred to be regulatory elements on single chromatin fibers

Outputs
- filtered.cram
    - CRAM file that contians all the data used in the FIRE pipeline
    - Can be viewed with IGV or other genome browsers

- peaks.bed.gz
    - Chrom: Chromosome peak is located on
    - peak*start: Start of peak
    - peah_end: End of peak
    - start: start of the maximum of the peka
    - end: end of the maximum of the peak
    - coverage: coverage of the peak
    - fire_coverage: coverage of the FIREs in the peak
    - fire_coverage: Coverage of the FIREs in the peak
    - score: FIRE score of the peak
    - nuc_coverage: Coverage of the nucleosomes in the peak
    - msp_coverage: Coverafge of the MSPs in the peak
    - .**{H1,H2}: Repeats of the nuc_coverage and msp_coverage but for the two haplotypes
    - FDR: False discovery rate of the peak

- {sample}-fire-{v}-hap.differences.bed.gz
    - Same as the previous file, but includes a p_value and p_adjust column that shows the difference in coverage between the two haplotypes

- {sample}-fire-{v}-pileup.bed.gz
    - BED file containing per-base information on the number of FIREs, MSPs, nucleosomes, coverage and more

- {sample}-fire-{v}-qc.tbl.gz
    - Contains quality control metrics for the FIRE CRAM

### HLA

HLA Genes
- Encode cell-surface proteins that help the immune system between the self and non-self
- Present antigens to T cells, triggering immune response

Outputs
- {sample}-fifihla_asm.contigs.h1.fasta.fai
    - Index file for the FASTQ
- {sample}-fifihla_asm.contigs.h1.fasta
    - Contains only the targeted HLA loci extracted from the full contigs
- {sample}-hifihla_report.tsv
    - Summary of HLA allele calls per locus
- {sample}-hifihla_report.json
    -  Detailed allele call information, including alignment stats, coverage, and differences

### PacBio WGS WDL

https://github.com/PacificBiosciences/HiFi-human-WGS-WDL

Outputs
- {sample}.length.nonref.counts.tsv
    - Counts of non-reference alleles at tandem repeat loci
- {sample}.length.nonref.tsv
    - More detailed version of above
    - Repeat locus coordinates, obsereved allele lengths, read support per allele
- {sample}.length.vcf.gz
    - Contains tandem repeat genotyping results
    - Genomic positions of tandem reapts. genotyped alleles, quality scores and annotations
- {sample}-spanning.bam
    - BAM file containing reads tha span tandem repeat regions
    - Enables visualization of repeat regions in genome browsers

### pacbiowdlR

https://scfurl.github.io/pacbiowdlR/index.html 

- Offers a suite of functions for visualizing and downstream processing of PacBio WGS WDL workflows

# Sunday, October 19th

## Exploring 9cl_seurat.rds with Seurat and Signac

https://zenodo.org/records/12209095 

https://stuartlab.org/signac/

https://satijalab.org/seurat/ 

{name} = readRDS("path_to_9cl_seurat.rds)

An object of class Seurat 
213408 features across 19737 samples within 4 assays 
Active assay: MotifMatrix (870 features, 0 variable features)
 2 layers present: counts, data
 3 other assays present: GeneExpressionMatrix, ATAC, GeneScoreMatrix
 2 dimensional reductions calculated: mo_UMAP, pca

Everything came from one cell line titled: EW?

library(VariantAnnotation)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)
library(org.Hs.eg.db)
library(biomaRt)

mart <- useMart("ensembl", dataset = "hsapiens_gene_ensembl")

bed_data <- getBM(
  attributes = c("external_gene_name", "chromosome_name", "start_position", "end_position"),
  filters = "external_gene_name",
  values = gene_list,
  mart = mart
)

# Wednesday, October 22th

## Creating a BED file of EwS Assiocated Genes

Used the R library readxl to convert the Excel file of EwS assiocated genes found through literature into R, then extracted the external gene name, chromosome name, start and end position for each EwS assiocated gene

There was an issue with some of the genes not being listed on canonical chromosomes, I had to remove these genes from the data set because they would have issues with future analysis down the line. 

The BED file was generated from
Dataset: hsapiens_gene_ensembl
Description: Human genes (GRCh38.p14)
Version: GRCh38.p14

These genes were: EHMT2, DYNC1I2, CDKN1C, DUX4

BED File generated called: EwSAscGenes.bed