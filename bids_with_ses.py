"""Heuristic to convert real-time schizophrenia data to BIDS format.

Adapted from Heudiconv example heuristic:
https://github.com/nipy/heudiconv/blob/master/heuristics/bids_with_ses.py

BIDS specification: http://bids.neuroimaging.io/bids_spec1.0.1.pdf
"""
from __future__ import print_function
import os


def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template, outtype, annotation_classes


def infotodict(seqinfo):
    """Heuristic evaluator for determining which runs belong where

    allowed template fields - follow python string module:

    item: index within category
    subject: participant id
    seqitem: run number during scanning
    subindex: sub index within group
    session: scan index for longitudinal acq
    """
    # print(seqinfo)

    # --- ANATOMICAL ---
    t1 = create_key('{session}/anat/sub-{subject}_{session}_T1w')
    t2 = create_key('{session}/anat/sub-{subject}_{session}_T2w')
    # --- TASK ---
    # Template
    # sub-<participant_label>[_ses-<session_label>]_task-<task_label>[_acq-<label>][_rec-<label>][_run-<index>]_bold.nii[.gz]
    rest = create_key('{session}/func/sub-{subject}_{session}_task-rest_acq-{direction}_bold')
    task = create_key('{session}/func/sub-{subject}_{session}_task-{task_name}_run-{item:02d}_bold')
    # --- Fieldmap ---
    spin_echo = create_key('{session}/fmap/sub-{subject}_{session}_dir-{direction}_epi')

    info = {t1: [], t2:[], rest:[], task:[], spin_echo:[],}
    last_run = len(seqinfo)

    for s in seqinfo:
        series_number = s[2]
        protocol_name = s[12]
        motion_corrected = s[13]
        x, y, sl, nt = (s[6], s[7], s[8], s[9])

        # --- ANATOMICAL ---
        # T1-weighted
        if (sl == 176 or sl == 704) and (nt == 1) and ('MEMPRAGE' in protocol_name):
            info[t1] = [series_number]
        # elif (nt == 1) and ('MEMPRAGE' in protocol_name):
        #     info[t1] = [series_number]
        # T2-weighted
        elif (sl == 176) and (nt == 1) and ('T2_SPACE' in protocol_name):
            info[t2] = [series_number]

        # --- FUNCTIONAL ---
        # Rest
        elif (sl == 65) and (nt == 300):
            if ('rffMRI_AP' in protocol_name):
                info[rest].append({'item': series_number, 'direction': 'AP'})
            elif ('rsfMRI_PA' in protocol_name):
                info[rest].append({'item': series_number, 'direction': 'PA'})
        # Tasks
        # QUESTION: are boolean-like strings converted to booleans in seqinfo?
        elif (sl == 32) and (nt == 136) and (motion_corrected == "True"):
            if ('fMRI_listen' in protocol_name):
                info[task_listen].append({'item': series_number, 'task_name': 'listen')
            elif ('fMRI_selfref' in protocol_name):
                info[task_listen].append({'item': series_number, 'task_name': 'selfref')
        # --- FIELDMAP ---
        # Spin Echo EPI
        elif (sl == 260) and (nt == 1):
            if ('Spin_Echo_EPI_AP' in protocol_name):
                info[spin_echo].append({'item': series_number, 'direction': 'AP'})
            elif ('Spin_Echo_EPI_PA' in protocol_name):
                info[spin_echo].append({'item': series_number, 'direction': 'PA'})
        else:
            pass

    return info
