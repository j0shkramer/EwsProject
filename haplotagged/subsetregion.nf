#!/usr/bin/env nextflow
nextflow.enable.dsl=2

process subsetBAM {    
    publishDir "EWSR1_FLI1_Fusion/", mode: 'copy'

    input:
        tuple val(name), path(bamfile), path(bai)

    
    output:
        path "EWSR1_FLI1.${name}.bam"

    script:
        """
        samtools view -b -h ${bamfile} chr11:128500000-128900000 chr22:29200000-29400000 > EWSR1_FLI1.${name}.bam
        """
}

process createBAI {
    publishDir "EWSR1_FLI1_Fusion/", mode: 'copy'

    input:
        path bam

    output:
        path "${bam}.bai"


    script:
        """
        samtools index ${bam}
        """
}

workflow {
    channel
        .fromFilePairs('haplotagged/*{bam,bam.bai}', flat: true)
        .set { bamPairs }

    smallerBAM = subsetBAM(bamPairs)

    createBAI(smallerBAM)
}