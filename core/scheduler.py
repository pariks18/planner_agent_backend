class Scheduler:
    def generate_schedule(self, tasks):
        schedule = []

        for i, task in enumerate(tasks):
            schedule.append({
                "task_id": task["id"],
                "task_name": task["name"],
                "day": i + 1
            })

        return schedule