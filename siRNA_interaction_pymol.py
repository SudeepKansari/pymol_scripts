#Usage: Keep the PDB files (Human AGO2-chain A + siRNA-chain B) in the same path as this script.
#Requisites: PyMOL should be in PATH; can be accessed by command line
#Command-
#python3 siRNA_interaction_pymol.py

import os
import pymol2

OUTPUT_DIR = "interactions"

CUTOFFS = {
    "h_bonds": 3.5,
    "salt_bridge": 4.0,
    "hydrophobic": 4.5,
    "vdw": 5.0,
    "cation_pi": 5.0,
    "pi_stack": 6.0,
}


def get_residue_pairs(cmd, selA, selB, cutoff):
    """Find unique residue pairs between two selections within cutoff"""
    pairs = set()

    # Get atoms from A near B
    model = cmd.get_model(f"({selA}) within {cutoff} of ({selB})")

    for atom in model.atom:
        resA = (atom.chain, atom.resn, atom.resi)

        # Find residues from B near this residue
        nearB = cmd.get_model(
            f"({selB}) within {cutoff} of (chain {atom.chain} and resi {atom.resi})"
        )

        for b in nearB.atom:
            resB = (b.chain, b.resn, b.resi)
            if resA[0] != resB[0]:
                pairs.add((resA, resB))

    return pairs


def analyze_interactions(pdb_path, cmd):
    name = os.path.splitext(os.path.basename(pdb_path))[0]

    cmd.reinitialize()
    cmd.load(pdb_path)

    interactions = {
        "h_bonds": "(name N* or name O*)",
        "salt_bridge": "(resn LYS or resn ARG or resn ASP or resn GLU)",
        "hydrophobic": "(resn ALA or resn VAL or resn LEU or resn ILE or resn PHE or resn PRO or resn MET)",
        "vdw": "all",
        "cation_pi": "(resn PHE or resn TYR or resn TRP or resn HIS or resn LYS or resn ARG)",
        "pi_stack": "(resn PHE or resn TYR or resn TRP or resn HIS)"
    }

    for interaction, selection in interactions.items():
        selA = f"chain A and {selection}"
        selB = "chain B"

        pairs = get_residue_pairs(cmd, selA, selB, CUTOFFS[interaction])

        out_file = os.path.join(OUTPUT_DIR, f"{name}_{interaction}.txt")
        with open(out_file, "w") as f:
            for (c1, r1, i1), (c2, r2, i2) in sorted(pairs, key=lambda x: (int(x[0][2]), int(x[1][2]))):
                f.write(f"{c1} {r1} {i1}  <-->  {c2} {r2} {i2}\n")

    print(f"✔ Interactions extracted for {name}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    pdbs = [f for f in os.listdir('.') if f.endswith('.pdb')]
    if not pdbs:
        print("No PDB files found.")
        return

    with pymol2.PyMOL() as pymol:
        cmd = pymol.cmd
        for pdb in pdbs:
            analyze_interactions(pdb, cmd)


if __name__ == "__main__":
    main()
