from llm.llm_interface import LLMInterface


class TaskDecomposer:

    def __init__(self):
        self.llm = LLMInterface()

    def decompose(self, goal):
        tasks = self.llm.generate_tasks(goal)
        return tasks