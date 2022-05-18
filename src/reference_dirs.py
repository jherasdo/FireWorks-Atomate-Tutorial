from atomate.vasp.fireworks.core import OptimizeFW, TransmuterFW
from atomate.vasp.firetasks.run_calc import RunVaspFake

# Reference dirs for RunVaspFake
path="/home/jovyan"
ref_dirs = {
    # Encut
    "Static-280-0": f"{path}/results/encut_calibration/280",
    "Static-300-1": f"{path}/results/encut_calibration/300",
    "Static-320-2": f"{path}/results/encut_calibration/320",
    "Static-340-3": f"{path}/results/encut_calibration/340",
    "Static-360-4": f"{path}/results/encut_calibration/360",
    "Static-380-5": f"{path}/results/encut_calibration/380",
    "Static-400-6": f"{path}/results/encut_calibration/400",
    "Static-420-7": f"{path}/results/encut_calibration/420",
    "Static-440-8": f"{path}/results/encut_calibration/440",
    "Static-460-9": f"{path}/results/encut_calibration/460",
    "Static-480-10": f"{path}/results/encut_calibration/480",
    "Static-500-11": f"{path}/results/encut_calibration/500",
    # EOS
    "structure_optimization": f"{path}/results/equation_of_states/structure_optimization",
    "bulk_deformation_0": f"{path}/results/equation_of_states/bulk_deformation_0",
    "bulk_deformation_1": f"{path}/results/equation_of_states/bulk_deformation_1",
    "bulk_deformation_2": f"{path}/results/equation_of_states/bulk_deformation_2",
    "bulk_deformation_3": f"{path}/results/equation_of_states/bulk_deformation_3",
    "bulk_deformation_4": f"{path}/results/equation_of_states/bulk_deformation_4",
    "bulk_deformation_5": f"{path}/results/equation_of_states/bulk_deformation_5",
    "bulk_deformation_6": f"{path}/results/equation_of_states/bulk_deformation_6",
    "bulk_deformation_7": f"{path}/results/equation_of_states/bulk_deformation_7",
    "bulk_deformation_8": f"{path}/results/equation_of_states/bulk_deformation_8",
    "bulk_deformation_9": f"{path}/results/equation_of_states/bulk_deformation_9",
    "bulk_deformation_10": f"{path}/results/equation_of_states/bulk_deformation_10",
    
    # Thickness
    "oriented_bulk": f"{path}/results/thickness_calibration/oriented_bulk",
    "slab_thickness_2": f"{path}/results/thickness_calibration/slab_thickness_2",
    "slab_thickness_3": f"{path}/results/thickness_calibration/slab_thickness_3",
    "slab_thickness_4": f"{path}/results/thickness_calibration/slab_thickness_4",
    "slab_thickness_5": f"{path}/results/thickness_calibration/slab_thickness_5",
    "slab_thickness_6": f"{path}/results/thickness_calibration/slab_thickness_6",
    # Adsorption Energy
    "adsorbate_box": f"{path}/results/adsorption_energy/adsorbate_box",
    "slab_ads_hollow_2": f"{path}/results/adsorption_energy/slab_ads_hollow_2",
    "slab_ads_bridge_1": f"{path}/results/adsorption_energy/slab_ads_bridge_1",
    "slab_ads_ontop_0": f"{path}/results/adsorption_energy/slab_ads_ontop_0",
}

class OptimizeFakeFW(OptimizeFW):
    def __init__(self, name, reference_dir, **kwargs):
        super(OptimizeFakeFW, self).__init__(name=name, **kwargs)
        
        self.name = name
        self.reference_dir = reference_dir
        self.tasks[1] = RunVaspFake(ref_dir=self.reference_dir[self.name], check_incar=False, check_potcar=False, check_kpoints=False)
        
        
class TransmuterFakeFW(TransmuterFW):
    def __init__(self, name, reference_dir, **kwargs):
        super(TransmuterFakeFW, self).__init__(name=name, **kwargs)
        
        self.name = name
        self.reference_dir = reference_dir
        self.tasks[1] = RunVaspFake(ref_dir=self.reference_dir[self.name], check_incar=False, check_potcar=False, check_kpoints=False)