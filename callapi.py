import requests
import json
import random

# API Base URL
BASE_URL = "https://betaapi.provideq.kit.edu" # "http://localhost:8080"

PRINT_REQUESTS = False

def get(endpoint):
    if PRINT_REQUESTS:
        print(f"GET {BASE_URL}{endpoint}")
    response = requests.get(f"{BASE_URL}{endpoint}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def post(endpoint, data):
    if PRINT_REQUESTS:
        print(f"POST {BASE_URL}{endpoint}")
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def patch(endpoint, data):
    if PRINT_REQUESTS:
        print(f"PATCH {BASE_URL}{endpoint}")
    headers = {'Content-Type': 'application/json'}
    response = requests.patch(f"{BASE_URL}{endpoint}", headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def create_problem(type, input, solverId):
    data = {'input': input, 'solverId': solverId}
    response = post(f"/problems/{type}", data)
    if response:
        return response['id']
    return None

def solve(problem_type, input, initial_solver_id, solver_per_type):
    starting_problem_id = create_problem(problem_type, input, initial_solver_id)

    problems = [(starting_problem_id, problem_type)]

    while True:
        start_problem = get(f"/problems/{problem_type}/{starting_problem_id}")
        if start_problem['state'] == "SOLVED":
            print("Problem solved", start_problem)
            break

        for (problem_id, type) in problems:
            problem = get(f"/problems/{type}/{problem_id}")

            if problem['state'] == "NEEDS_CONFIGURATION":
                solver_id = solver_per_type[problem['typeId']]()
                print("Start and set solver for", type, problem_id, "to", solver_id)
                patch(f"/problems/{type}/{problem['id']}", {"state": "SOLVING", "solverId": solver_id})

            if problem['state'] == "READY_TO_SOLVE":
                print("Start", type, problem_id)
                patch(f"/problems/{type}/{problem['id']}", {"state": "SOLVING"})

            if problem['state'] == "SOLVING":
                if problem['subProblems']:
                    for subproblem in problem['subProblems']:
                        # add subproblem to the list of problems to process if it is not already there
                        sub_type = subproblem['subRoutine']['typeId']
                        for sub in subproblem['subProblemIds']:
                            if not any(p[0] == sub for p in problems):
                                print("Add new subproblem to list", sub_type, sub)
                                problems.append((sub, sub_type))

def test_vrp_cluster_with_two_phase_solve_and_lkh_or_qrisp_qubo():
    vrp_input = """
    NAME : test
    TYPE : CVRP
    DIMENSION : 3
    EDGE_WEIGHT_TYPE : EUC_2D
    CAPACITY : 2
    NODE_COORD_SECTION
    1 0.00000 0.00000
    2 1.00000 0.50000
    3 0.50000 -1.00000
    DEMAND_SECTION
    1 0
    2 1
    3 2
    DEPOT_SECTION
    1
    -1
    """

    solver_per_type = {
        "vrp": lambda: "edu.kit.provideq.toolbox.vrp.solvers.ClusterAndSolveVrpSolver",
        "cluster-vrp": lambda: "edu.kit.provideq.toolbox.vrp.clusterer.TwoPhaseClusterer",
        "tsp": lambda: random.choice(
            ["edu.kit.provideq.toolbox.tsp.solvers.QuboTspSolver", "edu.kit.provideq.toolbox.tsp.solvers.LkhTspSolver"]),
        "qubo": lambda: "edu.kit.provideq.toolbox.qubo.solvers.QrispQuboSolver"
    }

    solve("vrp", vrp_input, "edu.kit.provideq.toolbox.vrp.solvers.ClusterAndSolveVrpSolver", solver_per_type)

test_vrp_cluster_with_two_phase_solve_and_lkh_or_qrisp_qubo()
