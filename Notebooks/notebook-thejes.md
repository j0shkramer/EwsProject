# Ewing Sarcoma Project

**Goal: Investigate chromatin structure and transcriptional programs in EwS**


## Week of 10/6

- Initial contact with collaborators
- 3 datasets:
    - scRNA-seq
    - scATAC-seq
    - Fiber-seq, long-read

## Week of 10/13

**9cl_seurat.rds**<br>
- Seurat dataset
- [Multiome dataset, Furlan lab](https://zenodo.org/records/12209095)
- [Github repo](https://github.com/furlan-lab/EwS_multiome)
- [Multimodal single-cell analyses reveal distinction fusion-regulated transcriptional programs in Ewing sarcoma](https://www.biorxiv.org/content/10.1101/2025.06.18.660457v1)
- Inspect Seurat object, with Seurat (scRNA-seq) and Signac (scATAC-seq)

Notes:
- Start looking at variants, assemble list of genes/genomic features with EwS associated variants
- Can query list as we find genes affected by structural variants, quickly tell if association is well-characterized or novel

---

Kobe initiated transfer of data onto Talapas (10/16)
- proj dir: /projects/bgmp/shared/groups/2025/sarcoma/
- data dir: /projects/bgmp/shared/groups/2025/sarcoma/shared
---

- Cell lines derived from patient samples
    - Fiber-seq
    - parallel scRNA/scATAC-seq
- Identify trends in gene expression, chromatin accessibility, and DNA methylation
- Data will most likely be given in processed form, will be responsible for initial QC filtering and analyzing datasets of sc data. 
- Fiber-seq will be in analyzable form

---
### R Resources

- [scRNA-seq, Seurat](https://satijalab.org/seurat/articles/get_started_v5_new)
- [scATAC-seq, Signac](https://github.com/GreenleafLab/ArchR)
- [scRNA + scATAC](https://stuartlab.org/signac/) combined data inside Seurat obj, use signac after
- [fiberseq](https://fiberseq.github.io/index.html)
- [Pacbio long read](https://github.com/PacificBiosciences/HiFi-human-WGS-WDL)

## Exploratory data analysis



### 9 EwS CL

| Cell line                  | Tumor site                       | Fusion type |
|----------------------------|----------------------------------|-------------|
| A673                       | Muscle                           | 1           |
| A4573                      | Pleural effusion                 | 3           |
| CHLA9 (isogenic w/ CHLA10) | Thoracic lymph node              | 1           |
| CHLA10 (isogenic w/ CHLA9)  | Thoracic lymph node              | 1           |
| PDX305                     | Abdominal soft-tissue metastatis | 1           |
| RDES                       | Humerus                          | 2           |
| SKNMC                      | Retroorbital metastatis          | 1           |
| TC32                       | Illeum and adjacent soft tissues | 1           |
| TC71                       | Humerus                          | 1           |



## Week of 10/20

- Vini and Josh will be tackling generating the bed files and filtering vcf based on list of genes from literature (EwS associated genes)

- I will then be taking the filtered lists and utilizing that in scRNA-seq analsis in Seurat for DGE visualizations

**Goals:**
- Establish/plan a workflow
    - What are vcf files?
    - What are bed files? 
    - How are they related? 
    - Whats the purpose and importance for next step?
- Determine way to use RStudio in Talapas

---

### RStudio/Docker/Talapas...

- Troubleshooting with Jason
- Issues with *loading* Seurat, was able to install
    - unable to load libglpk.so.40
    - Jason ended up creating new docker file with Seurat already installed
    - `run_rstudio-prod-v04-thejes.sh` 
        - working script, made adjustments for our data dir and my username
- Jason also helped me create ssh keys for local and Talapas, so I won't need to keep using DUO. Can also ssh into specific nodes 

--- 

## Sat 10/25

- Jason fixed issue with loading Seurat library in RStudio/Talapas
- `run_rstudio_prod-v04-thejes.sh`
    - slurm-39479566.out
```bash
cat slurm-39479566.out

# copy and paste into terminal LOCALLY
ssh -L 55881:localhost:58091 tnair@login4.talapas.uoregon.edu -t ssh -L 58091:localhost:55881 n0349.talapas.uoregon.edu

# in new browser copy and paste, will be prompted to log into RStudio
# username/pw noted in .sh

http://localhost:55881
...
```

---

## Mon 10/27 

Josh and Vini finished generating filtered vcf files<br>

files located:<br>
`/projects/bgmp/shared/groups/2025/sarcoma/shared/filtered_struc_variants`

Files were filtered from the .structural_variants.phased.vcf<br> files located in:<br>
`/projects/bgmp/shared/groups/2025/sarcoma/shared/250711_lewings_lines/pacbiowdlR`


Investigated filtered vcf files

```bash
zcat filtered.A673.GRCh38.structural_variants.phased.vcf.gz | grep -v "^#" | cut -f8 | grep -o "SVTYPE=[^;]*" | sort | u
niq -c
```

```bash
8 SVTYPE=BND
71 SVTYPE=DEL
9 SVTYPE=DUP
63 SVTYPE=INS
```

Josh created two files for me:
1. Filtered genes per cell line (.txt)
- this is what will be used in scRNA-seq analysis
- contains all genes falling w/i or affected by variants
- will contain first instance of gene (no variant info, no duplicates)

ex:<br>
AG73<br>
gene1<br>
gene2<br>
gene3<br>

2. Filtered genes, cell line, variant type (.txt)
- future analysis so we can interpret expression results in the context of variant types
- will have duplicates

    |Case | Description | Example|
    |---|---|---|
    | 1| 1 gene, multiple SVs | Deletion + Inversion in same gene|
    | 2 | 1 SV, multiple genes| Large deletion removes mult. genes |
    |3 | Many genes, many SVs| Chromothripsis, "chromosome shattering" |

ex:<br>
gene, cell line, variant<br>
gene1, A673, DEL

---

## Wed 10/29

- Inspecting Seurat object in RStudio via Docker/Talapas
()

List of cell lines and genes
`/projects/bgmp/shared/groups/2025/sarcoma/shared/filtered_struc_variants/celllinesgenes.tsv`

celllinesgenes.tsv currently formatted like:
```
cell line 1
gene 1
gene 2
gene 3
cell line 2
gene 1
gene 2
cell line 3
gene 1
```
For ease of analysis, reformat in R to:
```
cell_line gene
1   gene 1
1   gene 2
2   gene 3
3   gene 4
```

```bash
grep -n "CHLA9" celllinesgenes.tsv

108:CHLA9
```

Reorganized `celllinesgenes.tsv` > `genes_by_cellline_clean.tsv` <br>

cell_line corresponding gene

NOTE:<br>
- When loading RDS obj in RStudio, error message:
```
Approaching session memory limit. Session memory used: 3,878 MiB, Limit: 4,096 MiB. System memory used: 16,339 out of 257,024 MiB (93% free).
```

Will need to increase mem in .sh script? **Will talk to Jason**
For now, will subset one cell line

```bash
ls -lh 9cl_seurat.rds

2.8G
```
Because readRDS() decompresses .rds object, amount of memory it's taking up greatly increases. Will need to scancel, increase mem to maybe 32GB? and submit a new sbatch.

Can't even subset, R won't load the obj at all without crashing/terminating session.<br>
For the time being will try and do things on local R Studio. Downloaded .rds and _clean.tsv

```r
seurat_ob #loaded Seurat object

An object of class Seurat 
213408 features across 19737 samples within 4 assays 
Active assay: MotifMatrix (870 features, 0 variable features)
 2 layers present: counts, data
 3 other assays present: GeneExpressionMatrix, ATAC, GeneScoreMatrix
 2 dimensional reductions calculated: mo_UMAP, pca

```

**Features:** genes<br>
**Active assay:MotifMatrix (870 features, 0 variable features):** dataset focused on analysis of transcription factor binding motifs, no highly variable motifs have been identified<br>

---
## Thur 10/30

Hope mentioned when she used Seurat for clustering etc required 36-50 CPU depending on what she did.

- Seurat uses variable amounts of memory
- Integration + clustering can be mem intensive
- BUT looking at marker genes and making plots is not
- pre-processing : 50 cpus per task
- integration: 36
- finding clusters, marker genes: 50
- plots, doable on personal laptop

our data may be less intensive because similar and fr same species than what Hope was doing

Looked at data locally:
- grouped cell lines, associated genes
- turned df into vectored list for each cell
- subsetted one cell line, was going to look at that initially
- BUT actually need to integrate and cluster data first

**Integrate and cluster data before moving on to gene expression** 

```r
seurat_obj

An object of class Seurat 
213408 features across 19737 samples within 4 assays 
Active assay: MotifMatrix (870 features, 0 variable features)
 2 layers present: counts, data
 3 other assays present: GeneExpressionMatrix, ATAC, GeneScoreMatrix
 2 dimensional reductions calculated: mo_UMAP, pca
```

- 213408 features across 19737 samples
    - features: genes, peaks, motifs, etc
    - samples: cell lines
- active assay: MotifMatrix
    - what assay Seurat is using BY DEFAULT 
- obj can store multiple layers (assays), each a diff modality (omic data layer)

| Assay | Data Source | Measures | Description |
|--|--|--|--|
| MotifMatrix | derived from ATAC |Motif enrichment | TF activity |
| GeneExpressionMatrix| RNA | gene expression  | what genes are transcribed, normalized expression
| ATAC| raw open-chromatin reads| Chromatin accessibility/open regions | peaks|
| GeneScoreMatrix| ATAC derived | pseudo-gene counts, accessibility around promoter regions| which genes are accessible *potentially* active|


## Sun, Mon 11/02-11/03

will go back in and flesh out more

- inspected metadata
- default assay is MotifMatrix, set default to geneexpressionmatrix
- data is clustered
    - C1-25
- no need to run neighbors or findclusters
- mo_UMAP is based on geneexpressionmatrix data!!!
    - naming convention seems misleading at first
    - pca based on geneexpresisonmatrix data as well

- so can go ahead and run FindAllMarkers to find markers that define clusters
    - this will include up/downregulated genes
    - can use this immediately for identification of dge and later on for variant integration and pathway analysis
- figure out what plots to make, what would be the most informative. maybe just plot the top 5 and lowest 5? describe function of gene? not sure.

- next big step is integrating the .tsv file vini and josh made and see where there's overlap(?)

    - overlap gene list .tsv (see where rna clusters + variant affected genes)
    - compare w/i cell lines
    - compare ACROSS cell lines
    
    - pathway/GO enrichment (vini and josh)