cp /media/pw_synology3/PW_HiSeq_data/ChIP-seq/Mapped_data/176C/4196-27C-ZT10_S8/4196-27C-ZT10_S8_raw_bowtie2_TAIR10_ensembl_nomixed_sorted_rmdup_picard.bam \
  -t $PWD

samtools view -s 0.1 -b /media/pw_synology3/PW_HiSeq_data/ChIP-seq/Mapped_data/176C/INPUT-379_S21/INPUT-379_S21_raw_bowtie2_TAIR10_ensembl_nomixed_sorted_rmdup_picard.bam \
  > test__input.bam
