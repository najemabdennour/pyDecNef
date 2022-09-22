#############################################################################################
# AUTHORS: Pedro Margolles & David Soto
# EMAIL: pmargolles@bcbl.eu, dsoto@bcbl.eu
# COPYRIGHT: Copyright (C) 2021-2022, pyDecNef
# URL: https://pedromargolles.github.io/pyDecNef/
# INSTITUTION: Basque Center on Cognition, Brain and Language (BCBL), Spain
# LICENCE: GNU General Public License v3.0
#############################################################################################

#############################################################################################
# IMPORT DEPENDENCIES
#############################################################################################

import pandas as pd
from pathlib import Path
from nilearn.image import load_img, concat_imgs, new_img_like
from nilearn.input_data import NiftiMasker
import numpy as np

#############################################################################################
# DESCRIPTION
#############################################################################################

# Mask already preprocessed volumes of interest using extracted ROIs images for real time
# decoded neurofeedback

#############################################################################################
# SET FILE STRUCTURE
#############################################################################################

exp_dir = Path().absolute().parent.parent
data_dir = exp_dir / 'data'
preprocessed_dir = exp_dir / 'preprocessed/'
ref_vol_dir = preprocessed_dir / 'ref_vol'
vols_of_interest_dir = preprocessed_dir / 'preprocessed_vols_of_interest'
rois_dir = preprocessed_dir / 'ROIs_masks'
masked_vols_of_interest_dir = preprocessed_dir / 'masked_vols_of_interest'
rt_resources = data_dir / 'rt_resources'
rt_resources_zscoring = rt_resources / 'zscoring'

# Create dirs
masked_vols_of_interest_dir.mkdir(exist_ok = True, parents = True)
rt_resources_zscoring.mkdir(exist_ok = True, parents = True)

#############################################################################################
# SETUP VARIABLES
#############################################################################################

# Relevant variables for masking already preprocessed volumes of interest
ROI_mask = load_img(str(rois_dir / 'mask.nii.gz')) # ROI mask that will be used for masking volumes of interest

# ROI mask output name
ROI_mask_name = 'ROI'

#############################################################################################
# LOAD PRE-PROCESSED VOLUMES OF INTEREST, LABELS, INFORMATION FOR ZSCORING AND ROI MASK
#############################################################################################

preprocessed_vols_of_interest = load_img(str(vols_of_interest_dir / 'preprocessed_vols_of_interest.nii.gz')) # Preprocessed volumes of interest
mean_vols_of_interest = load_img(str(vols_of_interest_dir / 'mean_vols_of_interest.nii.gz')) # Whole-brain BOLD signal mean by voxel
std_vols_of_interest = load_img(str(vols_of_interest_dir / 'std_vols_of_interest.nii.gz')) # Whole-brain BOLD signal STD by voxel
labels_vols_of_interest = pd.read_csv(str(vols_of_interest_dir /  'labels_vols_of_interest.csv'))

#############################################################################################
# MAPPING VOLUMES' VOXELS IN THE WHOLE-BRAIN 3D SPACE TO MASKED 2D SPACE
#############################################################################################

ref_vol = ref_vol_dir / 'ref_vol_deobliqued_brain.nii'
ref_vol = load_img(str(ref_vol))

# Use NiLearn NiftiMasker class to convert whole-brain NiLearn images to masked flatten numpy arrays and restore original space if needed
# Using this trick you can easely map each voxel in the 3D space (i.e., NiLearn images) to the masked 2D space (i.e., masked flatten numpy arrays)
nifti_masker = NiftiMasker(mask_img = ROI_mask,
                           smoothing_fwhm = None, # Don't preprocess data at this point
                           standardize = False,  # Don't preprocess data at this point
                           detrend = False, # Don't preprocess data at this point
                           )

nifti_masker.fit(ref_vol) # Fit NiftiMasker to ref_vol dimensions

#############################################################################################
# MASK PREPROCESSED VOLUMES OF INTEREST
#############################################################################################

# Transform 4D Nilearn images to 2D numpy arrays
masked_preprocessed_vols_of_interest = nifti_masker.transform(preprocessed_vols_of_interest) # Mask preprocessed volumes of interest
masked_mean_vols_of_interest = nifti_masker.transform(mean_vols_of_interest) # Mask whole-brain BOLD signal mean by voxel
masked_std_vols_of_interest = nifti_masker.transform(std_vols_of_interest) # Mask whole-brain BOLD signal mean by voxel

# Save masked numpy arrays for model training and z-scoring data for volumes processing in real time
np.save(str(masked_vols_of_interest_dir / f'preprocessed_vols_of_interest_{ROI_mask_name}.npy'))
np.save(str(masked_vols_of_interest_dir / f'mean_vols_of_interest_{ROI_mask_name}.npy'))
np.save(str(masked_vols_of_interest_dir / f'std_vols_of_interest_{ROI_mask_name}.npy'))
labels_vols_of_interest.to_csv(str(masked_vols_of_interest_dir / f'labels_vols_of_interest.csv'))

# Copy z-scoring data for volumes processing in real time to rt_resources folder
np.save(str(rt_resources_zscoring / f'mean_vols_of_interest_{ROI_mask_name}.npy'))
np.save(str(rt_resources_zscoring / f'std_vols_of_interest_{ROI_mask_name}.npy'))