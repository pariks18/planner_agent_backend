class DependencyManager:

    def order_tasks(self, tasks):
        task_map = {task["id"]: task for task in tasks}
        in_degree = {task["id"]: 0 for task in tasks}
        graph = {task["id"]: [] for task in tasks}

        for task in tasks:
            for dep in task.get("dependencies", []):
                if dep not in task_map:
                    raise ValueError(f"Dependency {dep} not found")

                graph[dep].append(task["id"])
                in_degree[task["id"]] += 1

        queue = [tid for tid in in_degree if in_degree[tid] == 0]
        ordered = []

        while queue:
            current = queue.pop(0)
            ordered.append(task_map[current])

            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(ordered) != len(tasks):
            raise ValueError("Circular dependency detected")

        return ordered