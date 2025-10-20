from __future__ import annotations
import logging
from typing import Optional, Dict, List
from heudiconv.utils import SeqInfo

lgr = logging.getLogger("heudiconv")

def create_key(
    template: Optional[str],
    outtype: tuple[str, ...] = ("nii.gz",),
    annotation_classes: None = None,
):
    if template is None or not template:
        raise ValueError("Template must be a valid format string")
    return (template, outtype, annotation_classes)

# ======================================================================
# 1) Output keys — STANDARD BIDS PATHS with sub-/ses- everywhere
# ======================================================================
# ✅ 目录与文件名都改为直接用 {session}（不再拼 ses-）
func_bold = create_key(
    "sub-{subject}/{session}/func/sub-{subject}_{session}_task-social_run-{item:03d}_bold"
)
t1w = create_key(
    "sub-{subject}/{session}/anat/sub-{subject}_{session}_T1w"
)
fmap_ap = create_key(
    "sub-{subject}/{session}/fmap/sub-{subject}_{session}_dir-AP_epi"
)


# ======================================================================
# 2) Classification logic — kept same spirit (only templates changed)
#    Adjust the rules to your sequence names if needed.
# ======================================================================
def infotodict(seqinfo: List[SeqInfo]) -> Dict:
    info = {func_bold: [], t1w: [], fmap_ap: []}

    for s in seqinfo:
        pname = (s.protocol_name or "").lower()
        series_id = s.series_id

        # Functional BOLD (long time series)
        if "bold" in pname and (s.dim4 or 0) >= 60:
            info[func_bold].append({"item": series_id})
            lgr.info(f"Functional BOLD: {s.protocol_name} (run={series_id})")
            continue

        # T1w (single-volume structural; MPRAGE/VIBE etc.)
        if (("t1" in pname) or ("mprage" in pname)) and (s.dim4 or 1) == 1:
            info[t1w].append({"item": series_id})
            lgr.info(f"T1w: {s.protocol_name}")
            continue

        # Fieldmap EPI (short EPI series, assumed AP; tweak if needed)
        if ("epi" in pname or "fieldmap" in pname) and (s.dim4 or 0) in (8, 10, 12):
            info[fmap_ap].append({"item": series_id})
            lgr.info(f"Fieldmap EPI (AP): {s.protocol_name}")
            continue

        lgr.info(f"Unclassified: {s.protocol_name} (dim3={s.dim3}, dim4={s.dim4})")

    return info

# ======================================================================
# 3) IntendedFor population (closest match within same session)
# ======================================================================
POPULATE_INTENDED_FOR_OPTS = {
    "matching_parameters": ["Shims", "ImagingVolume"],
    "criterion": "Closest",
}
