import requests
import json

class ProvideQApi:
    def __init__(self, base_url, print_requests=False, print_debug=False):
        self.base_url = base_url
        self.print_requests = print_requests
        self.print_debug = print_debug

    def get(self, endpoint):
        if self.print_requests:
            print(f"GET {self.base_url}{endpoint}")
        response = requests.get(f"{self.base_url}{endpoint}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None

    def post(self, endpoint, data):
        if self.print_requests:
            print(f"POST {self.base_url}{endpoint}")
        headers = {'Content-Type': 'application/json'}
        response = requests.post(f"{self.base_url}{endpoint}", headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None

    def patch(self, endpoint, data):
        if self.print_requests:
            print(f"PATCH {self.base_url}{endpoint}")
        headers = {'Content-Type': 'application/json'}
        response = requests.patch(f"{self.base_url}{endpoint}", headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    
    def get_setting(self, settings_per_solver_id, solver_id):
        setting = dict.get(settings_per_solver_id, solver_id)
        if setting:
            return setting()
        
        return None

    def create_problem(self, type, input, solverId, settings_per_solver_id):
        data = {'input': input, 'solverId': solverId, 'solverSettings': self.get_setting(settings_per_solver_id, type)}
        response = self.post(f"/problems/{type}", data)
        if response:
            return response['id']
        return None

    def solve(self, problem_type, input, initial_solver_id, solver_per_type, settings_per_solver_id):
        starting_problem_id = self.create_problem(problem_type, input, initial_solver_id, settings_per_solver_id)

        problems = [(starting_problem_id, problem_type)]

        while True:
            start_problem = self.get(f"/problems/{problem_type}/{starting_problem_id}")
            if start_problem['state'] == "SOLVED":
                if self.print_debug:
                    print("Problem solved", start_problem)
                return start_problem['solution']

            for (problem_id, type) in problems:
                problem = self.get(f"/problems/{type}/{problem_id}")

                if self.print_debug:
                    print("Processing", problem)
                if problem['state'] == "NEEDS_CONFIGURATION":
                    solver_id = solver_per_type[problem['typeId']]()
                    if self.print_debug:
                        print("Start and set solver for", type, problem_id, "to", solver_id)
                    self.patch(f"/problems/{type}/{problem['id']}", {"state": "SOLVING", "solverId": solver_id, "solverSettings": self.get_setting(settings_per_solver_id, solver_id)})

                if problem['state'] == "READY_TO_SOLVE":
                    if self.print_debug:
                        print("Start", type, problem_id)
                    self.patch(f"/problems/{type}/{problem['id']}", {"state": "SOLVING"})

                if problem['state'] == "SOLVING":
                    if problem['subProblems']:
                        for subproblem in problem['subProblems']:
                            # add subproblem to the list of problems to process if it is not already there
                            sub_type = subproblem['subRoutine']['typeId']
                            for sub in subproblem['subProblemIds']:
                                if not any(p[0] == sub for p in problems):
                                    if self.print_debug:
                                        print("Add new subproblem to list", sub_type, sub)
                                    problems.append((sub, sub_type))
