from core.task_decomposer import TaskDecomposer
from core.dependency_manager import DependencyManager
from tools.resource_validator import ResourceValidator
from core.scheduler import Scheduler
from data.config import ROLE_GOAL_MAP


class PlannerAgent:

    def __init__(self):
        self.decomposer = TaskDecomposer()
        self.dep_manager = DependencyManager()
        self.scheduler = Scheduler()

    def plan(self, role: str, goal: str):

        # Step 1: Role Authorization Check
        allowed = ROLE_GOAL_MAP.get(role, [])
        if "*" not in allowed and goal not in allowed:
            raise PermissionError("Unauthorized role for this goal")

        # Step 2: Break goal into structured tasks
        tasks = self.decomposer.decompose(goal)

        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Reset resources for each full planning attempt
            validator = ResourceValidator()

            # Step 3: Order tasks based on dependencies
            ordered = self.dep_manager.order_tasks(tasks)

            invalid = []

            # Step 4: Validate and reserve resources
            for task in ordered:
                is_valid, details = validator.validate(task["name"])

                if not is_valid:
                    invalid.append((task, details))

            # If all tasks valid → break
            if not invalid:
                break

            # Simple retry: move invalid tasks to end
            for task, _ in invalid:
                ordered.remove(task)
                ordered.append(task)

            tasks = ordered

        else:
            raise Exception("Unable to resolve resource conflicts")

        # Step 5: Generate final schedule
        return self.scheduler.generate_schedule(ordered)