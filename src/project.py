"""Define the project's workflow logic and operation functions.

Execute this script directly from the command line, to view your project's
status, execute operations and submit them to a cluster. See also:

    $ python src/project.py --help
"""
import signac
from flow import FlowProject, directives
from flow.environment import DefaultSlurmEnvironment
import os


class MyProject(FlowProject):
    pass


class Borah(DefaultSlurmEnvironment):
    hostname_pattern = "borah"
    template = "borah.sh"

    @classmethod
    def add_args(cls, parser):
        parser.add_argument(
            "--partition",
            default="gpu",
            help="Specify the partition to submit to."
        )


class R2(DefaultSlurmEnvironment):
    hostname_pattern = "r2"
    template = "r2.sh"

    @classmethod
    def add_args(cls, parser):
        parser.add_argument(
            "--partition",
            default="gpuq",
            help="Specify the partition to submit to."
        )


class Fry(DefaultSlurmEnvironment):
    hostname_pattern = "fry"
    template = "fry.sh"

    @classmethod
    def add_args(cls, parser):
        parser.add_argument(
            "--partition",
            default="batch",
            help="Specify the partition to submit to."
        )

# Definition of project-related labels (classification)
@MyProject.label
def sampled(job):
    return job.doc.get("done")


@MyProject.label
def initialized(job):
    pass


@directives(executable="python -u")
@directives(ngpu=1)
@MyProject.operation
@MyProject.post(sampled)
def sample(job):
    import hoomd_polymers
    from hoomd_polymers.systems import Pack
    import hoomd_polymers.forcefields
    from hoomd_polymers.sim import Simulation
    import mbuild as mb
    import foyer

    with job:
        print("JOB ID NUMBER:")
        print(job.id)
        y6_file = "../../y6_typed.mol2"
        ff_file = "../../Y6.xml"

    def espaloma_mol(file_path, remove_hydrogens=False):
        mol = mb.load(file_path)
        if remove_hydrogens:
            h_atoms = [p for p in mol.particles_by_element(element="H")]
            for p in h_atoms:
                mol.remove(p)
        for p in mol.particles():
            p.name = f"_{p.name}"
        return mol

    y6_system = Pack(
            molecule=espaloma_mol,
            density=job.sp.density,
            n_mols=job.sp.n_compounds,
            mol_kwargs = {
                "file_path": y6_file,
                "remove_hydrogens": job.sp.remove_hydrogens
            },
            packing_expand_factor=5
    )

    y6_ff = foyer.Forcefield(forcefield_files=ff_file)
    y6_system.apply_forcefield(forcefield=y6_ff)

    job.doc.ref_distance = y6_system.references_values.distance
    job.doc.ref_mass = y6_system.references_values.mass
    job.doc.ref_energy = y6_system.references_values.energy

    y6_sim = Simulation(
        initial_state=y6_system.hoomd_snapshot,
        forcefield=y6_system.hoomd_forcefield,
        gsd_write_freq=5000
    )
    target_box = (y6_system.target_box*10)/job.doc.ref_distance
    job.doc.target_box = target_box

    y6_sim.run_update_volume(
            final_box=target_box,
            n_steps=job.sp.shrink_steps,
            period=job.sp.shrink_period,
            tau_kt=job.sp.tau_kt
    )
    y6_sim.run_NVT(kT=job.sp.kT, n_steps=job.sp.n_steps, tau_kt=job.sp.tau_kt)


if __name__ == "__main__":
    MyProject().main()
