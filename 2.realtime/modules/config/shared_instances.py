############################################################################
# AUTHORS: Pedro Margolles & David Soto
# EMAIL: pmargolles@bcbl.eu, dsoto@bcbl.eu
# COPYRIGHT: Copyright (C) 2021, Python fMRI-Neurofeedback
# INSTITUTION: Basque Center on Cognition, Brain and Language (BCBL), Spain
# LICENCE: 
############################################################################

#############################################################################################
# DESCRIPTION
#############################################################################################

# Here are indicated class objects instantiated in main.py which are then shared across all framework modules
# as global variables to facilitate processing in threads and returning results, and sychronization between modules

server = None # Corresponding class in modules/config/connection_config.py
new_trial = None # Corresponding class in modules/classes/classes.py
timeseries = None # Corresponding class in modules/classes/classes.py
new_vol = None # Corresponding class in modules/classes/classes.py
logger = None # Corresponding class in modules/classes/classes.py
plotter = None # Corresponding class in modules/classes/classes.py