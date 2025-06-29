import sys
import os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import pymol
from pymol import cmd

def main(pdb1_path, pdb2_path, residue_name):
    pymol.finish_launching(['pymol', '-q'])

    # Extract base names for object naming and output files
    pdb1_name = os.path.splitext(os.path.basename(pdb1_path))[0]
    pdb2_name = os.path.splitext(os.path.basename(pdb2_path))[0]

    # Load with original file base names as object names
    cmd.load(pdb1_path, pdb1_name)
    cmd.load(pdb2_path, pdb2_name)

    # Align target onto template
    cmd.align(pdb2_name, pdb1_name)

    # Show cartoon and make chains semi-transparent
    cmd.show("cartoon", pdb1_name)
    cmd.set("cartoon_transparency", 0.5, pdb1_name)
    cmd.show("cartoon", pdb2_name)
    cmd.set("cartoon_transparency", 0.5, pdb2_name)

    # Select residues of interest
    sel1 = f"{pdb1_name} and resn {residue_name}"
    sel2 = f"{pdb2_name} and resn {residue_name}"

    # Show sticks for selected residues
    cmd.show("sticks", sel1)
    cmd.show("sticks", sel2)

    # Color selections differently
    cmd.color("red", sel1)
    cmd.color("blue", sel2)

    # Label residues on CA atoms only (one label per residue)
    cmd.label(f"{sel1} and name CA", '"%s%s" % (resn, resi)')
    cmd.label(f"{sel2} and name CA", '"%s%s" % (resn, resi)')

    # Write residues to files, including chain in output for clarity
    def write_residues(selection, filename):
        seen = set()
        model = cmd.get_model(selection)
        with open(filename, "w") as f:
            for atom in model.atom:
                key = f"{atom.resn}{atom.resi}_{atom.chain}"
                if key not in seen:
                    seen.add(key)
                    f.write(key + "\n")

    write_residues(sel1, f"{pdb1_name}_residues.txt")
    write_residues(sel2, f"{pdb2_name}_residues.txt")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python get_residues.py <template.pdb> <target.pdb> <RESNAME>")
        sys.exit(1)
    pdb1_path, pdb2_path, resname = sys.argv[1], sys.argv[2], sys.argv[3].upper()
    main(pdb1_path, pdb2_path, resname)

cmd.sync()
