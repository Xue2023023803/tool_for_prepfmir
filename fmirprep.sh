sudo docker run --rm -it \
  -v /media/xue/xue/data:/data \
  -v /usr/local/freesurfer/7.4.1/license.txt:/opt/freesurfer/license.txt \
  nipreps/fmriprep \
  /data/BIDS_number /data/BIDS_prep participant \
  --bold2anat-init header \
  --skull-strip-fixed-seed \
  --bold2anat-dof 12 \
  --use-syn-sdc \
  --output-spaces  MNI152NLin2009cAsym:res-2 fsnative T1w \
  -w /data/work_prep
