import os
import pymol
from pymol import cmd



# Define function to execute interaction selection and extraction
def analyze_interactions(pdb_file, pathxn):
   # global result  # Declare the global result variable
    
    # Reinitialize PyMOL for each new pdb file to clear previous data
    cmd.reinitialize()
    
    # Load the PDB file into PyMOL
    cmd.load(pdb_file)
    
    # Define the selection commands
    interactions = {
        'h_bonds': "select h_bonds, (chain B and (name N* or name O*)) around 3.5",
        'hydrophobic': "select hydrophobic, (chain B and (resn ALA or resn LEU or resn ILE or resn PHE or resn VAL or resn PRO)) around 4.0",
        'salt_bridge': "select salt_bridge, (chain B and (resn LYS or resn ARG or resn GLU or resn ASP)) around 3.5",
        'vdw': "select vdw, (chain B) around 4.0",
        'cation_pi': "select cation_pi, (chain B and (resn PHE or resn TYR or resn HIS)) around 4.5",
        'pi_stack': "select pi_stack, (chain B and (resn PHE or resn TYR or resn TRP)) around 5.0"
    }


    # Iterate through each interaction type
    for interaction_name, select_cmd in interactions.items():
        cmd.do(select_cmd)  # Run the selection command
        
        pml_write(pathxn + pdb_file.replace(".pdb", ""), interaction_name)
        cmd.load("template.py")
    print(f'Generated output for {pdb_file}')


def pml_write(filename, interaction_name):
    const =["""    
import os
import pymol
from pymol import cmd
""", """
with open(""" + f'"{filename}_{interaction_name}.txt"' + ', "w") as output_file:',
"""
    # Iterate over a selection of atoms and write each atom's name and coordinates to the file
    cmd.iterate(""" +f'"{interaction_name}"' +""", 'output_file.write(f"Chain B: {resi}, {resn}, {chain}\\\\n")')
"""]

    with open("template.py", "w") as inp:
        inp.write("\n".join(const))


output_prefix = "output_dir/" #output_dir
# Loop through the PDB files in the working directory
working_directory = './'  # Make sure this is the correct working directory path
for pdb_file in os.listdir(working_directory):
    if pdb_file.endswith('.pdb'):  # Only process PDB files
        analyze_interactions(pdb_file, output_prefix)
