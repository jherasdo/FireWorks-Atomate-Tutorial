from atomate.vasp.database import VaspCalcDb

x = VaspCalcDb.from_db_file("/home/jovyan/atomate/config/db.json")
x.reset()

print("[SUCCESS] Connected to MongoDB.")
