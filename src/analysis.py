# Importing standard libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# PMG
import pymatgen
from pymatgen.core.structure import Structure
from pymatgen.core.surface import Slab
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
        
        # Units
        Ev2Joule = 16.0219  # eV/Angs2 to J/m2
        
        # DB
        db_file = env_chk(self.get("db_file"), fw_spec)
        to_db = self.get("to_db", True)
        
        # Summary Dict
        summary_dict = {}
        
        # Connect to the DB
        mmdb = VaspCalcDb.from_db_file(db_file, admin=True)
        
        # Collection and find documents
        d = mmdb.collection.find_one({"task_label": "oriented_bulk"})
        docs = mmdb.collection.find({"task_label": {"$regex": "slab_thickness_*"}})
        
        # Get energy and structure from oriented bulk
        oriented_bulk = Structure.from_dict(d["calcs_reversed"][-1]["output"]["structure"])
        oriented_bulk_energy = d["calcs_reversed"][-1]["output"]["energy"]
        bulk_comp = oriented_bulk.composition.as_dict()
        
        # Get the data dft energy and structure
        thickness_dict = {}
        for n, doc in enumerate(docs):
            # Get layer from task_label
            task_label = doc["task_label"]
            thickness = task_label.split("_")[2]
            
            # Structure and DFT energy
            struct = Structure.from_dict(doc["calcs_reversed"][-1]["output"]["structure"])
            dft_energy = doc["calcs_reversed"][-1]["output"]["energy"]
            
            # Re-build slab object
            slab_obj = Slab(
                        struct.lattice,
                        struct.species,
                        struct.frac_coords,
                        miller_index=[1,1,1],
                        oriented_unit_cell=oriented_bulk,
                        shift=0,
                        scale_factor=0,
                        energy=dft_energy)
            
            thickness_dict.update({str(thickness): slab_obj.as_dict()})
            
        # Append all slab_obj dict into summary_dict
        summary_dict["slab_objs"] = thickness_dict
        
        # Calc. surface energy for each thickness
        surface_energy_ev, surface_energy_j = {}, {}
        
        for layers, slab_obj in thickness_dict.items():
            # slab_obj as object
            slab_obj = Slab.from_dict(slab_obj)
            
            # slab_bulk_ratio
            slab_comp = slab_obj.composition.as_dict()
            slab_bulk_ratio = sum(slab_comp.values()) / sum(bulk_comp.values())
            
            # Surface energy eV/angs2
            gamma_ev = self.get_surface_energy(slab_obj.energy, 
                                              oriented_bulk_energy,
                                              slab_bulk_ratio,
                                              slab_obj.surface_area)
            
            gamma_j = round(gamma_ev * Ev2Joule, 4)
            
            # Append to dict
            surface_energy_ev.update({str(layers): round(gamma_ev, 4)})
            surface_energy_j.update({str(layers): gamma_j})
            
        # Append to summary dict
        summary_dict["gamma_ev"] = surface_energy_ev
        summary_dict["gamma_j"] = surface_energy_j
        
        # Add results to DB
        if to_db:
            mmdb.collection = mmdb.db["thickness"]
            mmdb.collection.insert_one(summary_dict)
            
        # Plot
        fig = plt.figure(figsize=(8,8))
        
        plt.xlabel("Number of Layers")
        plt.ylabel("Surface Energy [J/m2]")
        
        n_layers = [int(i) for i in surface_energy_j.keys()]
        plt.xticks(n_layers)
        
        plt.scatter(n_layers, surface_energy_j.values(), marker="s", color="black")
        
        plt.savefig("Pt_111_thickness.png", dpi=100, facecolor="white", transparent=False)
        
        # Logger
        logger.info("Thickness Calibration Completed!")
        
        return
            
    def get_surface_energy(self, slab_E, oriented_E, slab_bulk_ratio, slab_area):
        """Get the surface energy"""
        gamma_hkl = (slab_E - (slab_bulk_ratio * oriented_E)) / (2 * slab_area)
        return gamma_hkl
    
    
    
@explicit_serialize
class AdsoptionEnergyTask(FiretaskBase):
    
    _fw_name = "Adsorption Energy Task"
    
    required_params = ["thickness", "db_file"]
    optional_params = ["to_db"]
    
    def run_task(self, fw_spec):
        
        # DB
        db_file = env_chk(self.get("db_file"), fw_spec)
        to_db = self.get("to_db", True)
        
        # Thickness
        slab_thickness = self["thickness"]
        
        # Summary Dict
        summary_dict = {}
        
        # Connect to the DB
        mmdb = VaspCalcDb.from_db_file(db_file, admin=True)
        
        # Collection and find documents
        doc_ads_box = mmdb.collection.find_one({"task_label": "adsorbate_box"})
        
        doc_oriented_bulk = mmdb.collection.find_one({"task_label": "oriented_bulk"})
        docs = mmdb.collection.find({"task_label": {"$regex": "slab_ads_*"}})
        
        # Adsorbate in box structure and DFT energy
        ads_box_struct = Structure.from_dict(doc_ads_box["calcs_reversed"][-1]["output"]["structure"])
        ads_box_energy = doc_ads_box["calcs_reversed"][-1]["output"]["energy"]
        
        summary_dict["ads_box_struct"] = ads_box_struct.as_dict()
        summary_dict["ads_box_energy"] = ads_box_energy
        
        # We need the oriented bulk to re-build the slab object
        oriented_bulk = Structure.from_dict(doc_oriented_bulk["calcs_reversed"][-1]["output"]["structure"])
        
        # We also need the clean surface with the right thickness
        thick_collection = mmdb.db["thickness"]
        thick_doc = thick_collection.find({})[0]
        
        slab_clean_dict = thick_doc["slab_objs"]
        slab_clean = Slab.from_dict(slab_clean_dict[str(slab_thickness)])
        
        
        # Slab_ads structures and energies
        slab_ads_dict = {}
        for n, doc in enumerate(docs):
            # Get ads_label from task_label
            task_label = doc["task_label"]
            ads_label = task_label.split("_")[2]
            
            # Struct and DFT energy
            struct = Structure.from_dict(doc["calcs_reversed"][-1]["output"]["structure"])
            dft_energy = doc["calcs_reversed"][-1]["output"]["structure"]
            
            # Slab_obj
            slab_obj = Slab(
                        struct.lattice,
                        struct.species,
                        struct.frac_coords,
                        miller_index=[1,1,1],
                        oriented_unit_cell=oriented_bulk,
                        shift=0,
                        scale_factor=0,
                        energy=dft_energy)
            
            # Append to slab_ads_dict
            slab_ads_dict.update({str(ads_label): slab_obj.as_dict()})
            
        # Append to summary dict
        summary_dict["slab_ads"] = slab_ads_dict
        
        # Adsorption energies
        e_ads_dict = {}
        for label, slab_ads in slab_ads_dict.items():
            # slab_ads as object
            slab_ads = Slab.from_dict(slab_ads)
            
            # Adsorption energy
            e_ads = self.get_adsorption_energy(slab_ads.energy, slab_clean.energy, ads_box_energy)
            
            # Append to dict
            e_ads_dict.update({str(label): e_ads})
            
            # Logger
            logger.info(f"Adsorption energy at {label} site: {e_ads} [eV]")
            
        # Append to summary dict
        summary_dict["e_ads"] = e_ads_dict
            
        
        # Add results to DB
        if to_db:
            mmdb.collection = mmdb.db["E_ads"]
            mmdb.collection.insert_one(summary_dict)
            
            
        # Logger
        logger.info("Adsorption Energy Analysis Completed!")
        
        return

            
    def get_adsorption_energy(self, slab_ads_e, slab_clean_e, adsorbate_e):
        
        e_ads = (slab_ads_e - slab_clean_e - adsorbate_e)
        
        return e_ads