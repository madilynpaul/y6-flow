#!/usr/bin/env python
"""Initialize the project's data space.

Iterates over all defined state points and initializes
the associated job workspace directories.
The result of running this file is the creation of a signac workspace:
    - signac.rc file containing the project name
    - signac_statepoints.json summary for the entire workspace
    - workspace/ directory that contains a sub-directory of every individual statepoint
    - signac_statepoints.json within each individual statepoint sub-directory.

"""

import signac
import logging
from collections import OrderedDict
from itertools import product


def get_parameters():
    '''
    '''
    parameters = OrderedDict()

    ### SYSTEM GENERATION PARAMETERS ###
    parameters["molecule"] = ["PPS"]
    parameters["molecule_kwargs"] = [None]
    parameters["system_seed"] = [24]
    parameters["system_type"] = ["Pack"]
    parameters["density"] = [1.35]
    parameters["n_compounds"] = [25]
    parameters["system_kwargs"] = [None]
    parameters["forcefield"] = ["OPLS_AA_PPS"]
    parameters["remove_hydrogens"] = [True]

    ### SIM FROM RESTART PARAMETERS ###
    parameters["restart_file"] = [None]

    ### SIMULATION PARAMETERS ###
    parameters["methods"] = ["run_update_volume", "run_NVT"]
    parameters["tau_kt"] = [0.1]
    parameters["tau_p"] = [None]
    parameters["pressure"] = [None]
    parameters["dt"] = [0.0003]
    parameters["r_cut"] = [2.5]
    parameters["sim_seed"] = [42]
    parameters["neighbor_list"] = ["Cell"]
    parameters["walls"] = [None]
    parameters["init_shrink_kT"] = [7]
    parameters["final_shrink_kT"] = [7]
    parameters["shrink_steps"] = [1e6]
    parameters["shrink_period"] = [1]
    ### Quench related parameters ###
    parameters["kT_quench"] = [7]
    parameters["n_steps"] = [2e5]

def main():
    project = signac.init_project() # Set the signac project name
    param_names, param_combinations = get_parameters()
    # Create the generate jobs
    for params in param_combinations:
        parent_statepoint = dict(zip(param_names, params))
        parent_job = project.open_job(parent_statepoint)
        parent_job.init()
        parent_job.doc.setdefault("done", False)

    project.write_statepoints()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
