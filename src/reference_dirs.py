from atomate.vasp.fireworks.core import OptimizeFW
from atomate.vasp.firetasks.run_calc import RunVaspFake

# Reference dirs for RunVaspFake
reference_dirs = {
    # Encut
    "Static-280-0": "../results/encut_calibration/280",
    "Static-300-1": "../results/encut_calibration/300",
    "Static-320-2": "../results/encut_calibration/320",
    "Static-340-3": "../results/encut_calibration/340",
    "Static-360-4": "../results/encut_calibration/360",
    "Static-380-5": "../results/encut_calibration/380",
    "Static-400-6": "../results/encut_calibration/400",
    "Static-420-7": "../results/encut_calibration/420",
    "Static-440-8": "../results/encut_calibration/440",
    "Static-460-9": "../results/encut_calibration/460",
    "Static-480-10": "../results/encut_calibration/480",
    "Static-500-11": "../results/encut_calibration/500",
    # EOS
    "structure_optimization": "../results/eos/bulk_optimization",
    "bulk_deformation_1": "../results/eos/bulk_deformation_1",
    "bulk_deformation_2": "../results/eos/bulk_deformation_2",
    "bulk_deformation_3": "../results/eos/bulk_deformation_3",
    "bulk_deformation_4": "../results/eos/bulk_deformation_4",
    "bulk_deformation_5": "../results/eos/bulk_deformation_5",
    "bulk_deformation_6": "../results/eos/bulk_deformation_6",
    "bulk_deformation_7": "../results/eos/bulk_deformation_7",
    "bulk_deformation_8": "../results/eos/bulk_deformation_8",
    "bulk_deformation_9": "../results/eos/bulk_deformation_9",
    "bulk_deformation_10": "../results/eos/bulk_deformation_10",
    # Thickness
    "oriented_bulk": "../results/thickness_calibration/",
    "slab_thickness_2": "../results/thickness_calibration/slab_thickness_2",
    "slab_thickness_3": "../results/thickness_calibration/slab_thickness_3",
    "slab_thickness_4": "../results/thickness_calibration/slab_thickness_4",
    "slab_thickness_5": "../results/thickness_calibration/slab_thickness_5",
    "slab_thickness_6": "../results/thickness_calibration/slab_thickness_6",
    # Adsorption Energy
    "adsorbate_box": "../results/adsorption_energy/",
    "slab_ads_hollow_2": "../results/adsorption_energy/hollow",
    "slab_ads_bridge_1": "../results/adsorption_energy/bridge",
    "slab_ads_ontop_0": "../results/adsorption_energy/ontop",
}

class OptimizeFakeFW(OptimizeFW):
    def __init__(self, reference_dir):
        super(OptimizeFakeFW, self).__init__()
        
        self.reference_dir = reference_dir
        self.tasks[1] = RunVaspFake(ref_dir=reference_dir[self.name], check_potcar=False)