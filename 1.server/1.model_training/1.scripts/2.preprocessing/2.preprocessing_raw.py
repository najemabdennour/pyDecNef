#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# NOTES
# Before running load dcm2niix and AFNI first in the cluster
# Change brainextraction.inputs.clfrac to improve brain extraction

# IMPORT BASIC DEPENDENCIES
from pathlib import Path
from nipype.interfaces import afni as afni
import shutil
import subprocess

# SET FILE STRUCTURE
###################################################
### najem addons
import os
exp_dir = os.path.abspath(os.path.join(os.path.abspath(__file__),os.pardir,os.pardir,os.pardir) )    #Path().absolute() 
raw_vols_dir = os.path.join(exp_dir, '2.data/raw/func/')
raw_vols_dir = Path(raw_vols_dir)
preprocessed_dir =Path(os.path.join(exp_dir,,'2.data', 'preprocessed'))
###
###################################################
func_dir = preprocessed_dir / 'func'
func_dir.mkdir(exist_ok = True, parents = True)
example_func_dir = preprocessed_dir / 'example_func'
example_func = str(example_func_dir / 'example_func_deoblique_brain.nii')

# PREPROCESS RAW VOLS
for folder in raw_vols_dir.iterdir():
    if folder.is_dir():
        run_dir = func_dir / folder.stem
        run_dir.mkdir(exist_ok = True, parents = True)
        
        #for vol_file in folder.glob('*.dcm'):
        for vol_file in folder.glob('*.dcm'):
            
            # Load vol DICOM, convert to Nifti and store the result in run_dir
            vol_name = vol_file.stem
            subprocess.run([f'dcm2niix -z n -f {vol_name} -o {run_dir} -s y {vol_file}'], shell = True)
            nifti_file = run_dir / (vol_name + '.nii') # To save each vol as .nii instead to .nii.gz to load faster
                                        
            # Deoblique converted Nifti file
            deoblique = afni.Warp() # Use AFNI 3dWarp command
            deoblique.inputs.in_file = nifti_file
            deoblique.inputs.deoblique = True # Deoblique Nifti files
            deoblique.inputs.gridset = example_func # Copy train_reference_vol grid so vols dimensions match between sessions
            deoblique.inputs.num_threads = 4 # Set number of threads for processing
            deoblique.inputs.outputtype = 'NIFTI'
            deoblique_file = run_dir / (vol_name + '_deoblique.nii')
            deoblique.inputs.out_file = deoblique_file
            deoblique.run()
            
            # Perform brain extraction to improve session to session registration of functional data
            brainextraction = afni.Automask() # Use AFNI Automask command
            brainextraction.inputs.in_file = deoblique_file
            brainextraction.inputs.erode = 1 # Erode the mask inwards to avoid skull and tissue fragments. Check this parameter for each subject based on brain extraction performance during training session.
            brainextraction.inputs.clfrac = 0.5 # Sets the clip level fraction (0.1 - 0.9). By default 0.5. The larger the restrictive brain extraction is.
            brainextraction.inputs.num_threads = 4 # Set number of threads for processing
            brainextraction.inputs.outputtype = 'NIFTI'
            brain_file = run_dir / (vol_name + '_deoblique_brain.nii')
            brainmask_file = run_dir / (vol_name + '_deoblique_brainmask.nii')
            brainextraction.inputs.brain_file = brain_file # Just brain's data
            brainextraction.inputs.out_file = brainmask_file # Brain binarized mask
            brainextraction.run()
        
            # Corregister test func vol brain to train reference vol brain
            volreg = afni.Volreg() # Use AFNI 3dvolreg command
            volreg.inputs.in_file = brain_file
            volreg.inputs.basefile = example_func # Take train_reference_vol as base file for registration
            volreg.inputs.args = '-heptic' # Spatial interpolation
            volreg.inputs.num_threads = 4 # Set number of threads for processing
            volreg.inputs.outputtype = 'NIFTI'
            oned_file = run_dir / (vol_name + '_deoblique_brain_corregister.1D') 
            oned_matrix_file =  run_dir / (vol_name + '_deoblique_brain_corregister.aff12.1D')
            md1d_file = run_dir / (vol_name + '_deoblique_brain_corregister_md.1D')
            corregister_file = run_dir / (vol_name + '_deoblique_brain_corregister.nii')
            volreg.inputs.oned_file = oned_file # 1D movement parameters output file -1Dfile
            volreg.inputs.oned_matrix_save = oned_matrix_file # Save the matrix transformation. -1Dmatrix_save
            volreg.inputs.md1d_file = md1d_file # Max displacement output file -maxdisp1D
            volreg.inputs.out_file = corregister_file # Corregistered vol
            volreg.run()
            
            for file in run_dir.glob('*'): # To save space, remove all files from preprocessed runs folders which does not contain 'corregister.nii' string in their name
                if 'corregister.nii' not in str(file):
                    file.unlink()
