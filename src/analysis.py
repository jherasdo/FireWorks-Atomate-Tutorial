# Importing standard libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# PMG
import pymatgen
from pymatgen.core.structure import Structure
from pymatgen.analysis.eos import EOS

# FireWorks and Atomate
from pydash.objects import has, get
from atomate.vasp.fireworks.core import OptimizeFW, TransmuterFW, StaticFW
from atomate.vasp.config import VASP_CMD, DB_FILE
from fireworks import FiretaskBase, Firework, Workflow, explicit_serialize, LaunchPad
from fireworks.utilities.fw_serializers import DATETIME_HANDLER
from atomate.utils.utils import env_chk, get_logger
from atomate.vasp.database import VaspCalcDb
from fireworks.core.rocket_launcher import rapidfire

# Logger
logger = get_logger(__name__)


# Post-processing Firetask to plot Encut calibration
@explicit_serialize
class PlotEncutCalib(FiretaskBase):

    _fw_name = "Plot Encut Calib"
    
    required_params = ["db_file"]
    optional_params = ["to_db"]
    
    def run_task(self, fw_spec):
        # DB
        db_file = env_chk(self.get("db_file"), fw_spec)
        to_db = self.get("to_db", True)
        
        # Connect to the DB
        mmdb = VaspCalcDb.from_db_file(db_file, admin=True)
        
        # Find the Static calculations
        docs = mmdb.collection.find({'task_label': {"$regex": ".*Static-*"}})
        
        # Loop over static calculations to get DFT Energy
        encuts, energies = [], []
        for n, doc in enumerate(docs):
            encut = doc["orig_inputs"]["incar"]["ENCUT"]
            dft_energy = doc["calcs_reversed"][-1]["output"]["energy"]
            encuts.append(encut)
            energies.append(dft_energy)
            
        # Plot
        fig = plt.figure(figsize=(8,8))
        
        plt.xlabel("Cut-off (eV)", fontsize=12, fontweight="bold")
        plt.ylabel("E/atom (eV)", fontsize=12, fontweight="bold")
        
        plt.xticks(encuts)
        
        plt.scatter(encuts, energies, marker="s", color="black")
        
        plt.savefig("Pt_encut_calib.png", dpi=100, facecolor="white", transparent=False)
        
        # Logger
        logger.info("Calibration Plot Finished!")
        
        return
        

@explicit_serialize
class FitEOSTask(FiretaskBase):
    
    _fw_name = "Fit EOS Task"
    
    required_params = ["eos", "db_file"]
    optional_params = ["to_db"]
    
    def run_task(self, fw_spec):
        
        # DB
        db_file = env_chk(self.get("db_file"), fw_spec)
        to_db = self.get("to_db", True)
        
        # EOS
        eos = fw_spec.get("eos", "vinet")
        summary_dict = {"eos": eos}
        
        # Connect to the DB
        mmdb = VaspCalcDb.from_db_file(db_file, admin=True)
        
        # Collection optimized and Deformations documents
        d = mmdb.collection.find_one({"task_label": {"$regex": ".*structure_optimization"}})
        docs = mmdb.collection.find({"task_label": {"$regex": "bulk_deformation_*"}})
        
        # Get the optimized structure as template
        structure_dict = d["calcs_reversed"][-1]["output"]["structure"]
        structure = Structure.from_dict(structure_dict)

        # Get the data (energy, volume) from deformations
        energies, volumes = [], []
        for n, doc in enumerate(docs):
            s = Structure.from_dict(doc["calcs_reversed"][-1]["output"]["structure"])
            dft_energy = doc["calcs_reversed"][-1]["output"]["energy"]
            energies.append(dft_energy)
            volumes.append(s.volume)

        # Fit the EOS
        eos = EOS(eos_name=eos)
        eos_fit = eos.fit(volumes, energies)

        # Logger
        logger.info(f"Equilibrium Volume: {eos_fit.v0} - Equilibrium Energy: {eos_fit.e0}")

        # Scale optimized structure to Eq. Volume
        structure.scale_lattice(eos_fit.v0)
        
        # Appending info into summary_dict
        summary_dict["energies"] = energies
        summary_dict["volumes"] = volumes
        summary_dict["volume_eq"] = eos_fit.v0
        summary_dict["energy_eq"] = eos_fit.e0
        summary_dict["structure_eq"] = structure.as_dict()

        # Add results to DB
        if to_db:
            mmdb.collection = mmdb.db["eos"]
            mmdb.collection.insert_one(summary_dict)

        # Plot
        eos_plot = eos_fit.plot()
        eos_plot.savefig("equation_of_states.png", dpi=100)

        # Logger
        logger.info("EOS Fitting Completed!")
        
        return

@explicit_serialize
class SlabThicknessTask(FiretaskBase):
    
    _fw_name = "Slab Thickness Calibration Task"
    
    required_params = ["db_file"]
    optional_params = ["to_db"]
    
    def run_task(self, fw_spec):
        
        # DB
        db_file = env_chk(self.get("db_file"), fw_spec)
        to_db = self.get("to_db", True)
        
        # Summary Dict
        summary_dict = {}
        
        
        # Connect to the DB
        mmdb = VaspCalcDb.from_db_file(db_file, admin=True)
        
        # Collection and find documents
        docs = mmdb.collection.find({"task_label": {"$regex": ".*slab_thickness_*"}})
        
        # Get the data dft energy and structure
        for n, doc in enumerate(docs):
            struct = Structure.from_dict(doc["calcs_reversed"][-1]["output"]["structure"])
            dft_energy = doc["calcs_reversed"][-1]["output"]["energy"]
            
        
        
        
        return