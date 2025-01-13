## Example API Usage Script

This script can be called to automatically invoke the [ProvideQ API](https://github.com/ProvideQ/toolbox-server).
You use this to solve any kind of problem with a set of pre-defined solvers.

### Example
```python
# Solvers for subroutines
solver_per_type = {
    "cluster-vrp": lambda: "edu.kit.provideq.toolbox.vrp.clusterer.TwoPhaseClusterer",
    "tsp": lambda: "edu.kit.provideq.toolbox.tsp.solvers.LkhTspSolver"
}

settings_per_solver_id = {
    "edu.kit.provideq.toolbox.vrp.clusterer.KmeansClusterer": lambda: [
        {
            "name": "Cluster Number",
            "type": "INTEGER",
            "required": False,
            "description": "",
            "min": 1,
            "max": 1000,
            "value": 3,
        }
    ],
}

solve("vrp", "<some_vrp_input>", "edu.kit.provideq.toolbox.vrp.solvers.ClusterAndSolveVrpSolver", solver_per_type, settings_per_solver_id)
```
