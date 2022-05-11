# Importing standard libraries
import numpy as np

# PMG
import pymatgen
from pymatgen.io.vasp.sets import MVLSlabSet
from pymatgen.io.vasp.inputs import Kpoints


# Create the DFT Theoretical level
class TheoreticalLevelSet(MVLSlabSet):
    """Custom VASP input set"""
    
    def __init__(self, structure, psp_version="PBE_54", bulk=False, **kwargs):
        super(TheoreticalLevelSet, self).__init__(structure, bulk=bulk, **kwargs)
        
        self.psp_version = psp_version
        self.bulk = bulk
        
        # Change the default PBE version from PMG
        psp_versions = ["PBE", "PBE_52", "PBE_54"]
        assert self.psp_version in psp_versions
        self.potcat_functional = "PBE_54"
        
    @property
    def incar(self):
        incar = super(TheoreticalLevelSet, self).incar
        
        # Direct or reciprocal
        if self.bulk:
            incar["LREAL"] = False
        else:
            incar["LREAL"] = True
            
        # Non-spin polarized
        incar.pop("MAGMOM")
        
        # INCAR Settings
        incar_config = {
            "PREC": "Normal",
            "ALGO": 38,
            "GGA": "RP",
            "ENCUT": 350.0,
            "EDIFFG": -0.03,
            "EDIFF": 0.1e-03,
            "ISPIN": 1,
            "IBRION": 2,
            "NSW": 200,
            "ISIF": 0,
            "ISYM": 0,
            "SYMPREC": 1e-6,
            "LWAVE": False,
            "LASPH": False,
            "LVTOT": False,
            "NCORE": 4,
            "NELMIN": 4,
            "NELM": 60,
            "ISMEAR": 0,
            "SIGMA": 0.05,
        }
        
        # Update INCAR
        incar.update(incar_config)
        incar.update(self.user_incar_settings)
        return incar
    
    @property
    def kpoints(self):
        abc = np.array(self.structure.lattice.abc)
        
        if self.bulk:
            return Kpoints.gamma_automatic((8,8,8))
        
        else:
            return Kpoints.gamma_automatic((4,4,1))