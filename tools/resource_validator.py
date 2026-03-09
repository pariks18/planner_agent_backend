class ResourceValidator:
    """
    Validates AND reserves resources for construction tasks.
    """

    def __init__(self):
        # Mock resource inventory (can later come from DB/API)
        self.available_resources = {
            "labor": {
                "engineer": 200,
                "worker": 120,
                "electrician": 2000,
                "plumber": 100,
            },
            "equipment": {
                "excavator": 100,
                "crane": 100,
                "concrete_mixer": 200,
            },
            "materials": {
                "cement": 10000,
                "steel": 5000,
                "bricks": 20000,
            },
        }

    # -----------------------------
    # Task → Resource Mapping
    # -----------------------------
    def _required_resources(self, task: str):
        """
        Determines resources required for a task.
        """
        task = task.lower()

        if "excavation" in task:
            return {
                "labor": {"worker": 5},
                "equipment": {"excavator": 1},
                "materials": {},
            }

        elif "foundation" in task:
            return {
                "labor": {"engineer": 1, "worker": 6},
                "equipment": {"concrete_mixer": 1},
                "materials": {"cement": 30, "steel": 15},
            }

        elif "brickwork" in task or "wall" in task:
            return {
                "labor": {"worker": 6},
                "equipment": {},
                "materials": {"bricks": 500, "cement": 10},
            }

        elif "electrical" in task:
            return {
                "labor": {"electrician": 1},
                "equipment": {},
                "materials": {},
            }

        elif "plumbing" in task:
            return {
                "labor": {"plumber": 1},
                "equipment": {},
                "materials": {},
            }

        # default small task
        return {
            "labor": {"worker": 2},
            "equipment": {},
            "materials": {},
        }

    # -----------------------------
    # Resource Checking
    # -----------------------------
    def _check_category(self, required, available):
        """
        Checks if required resources are available.
        Returns missing resources if any.
        """
        missing = {}

        for resource, qty in required.items():
            if available.get(resource, 0) < qty:
                missing[resource] = qty - available.get(resource, 0)

        return missing

    # -----------------------------
    # Reserve Resources
    # -----------------------------
    def _reserve_resources(self, required):
        """
        Deducts used resources from inventory.
        (NEW ADDITION — This fixes the earlier logical flaw)
        """
        for category in required:
            for resource, qty in required[category].items():
                self.available_resources[category][resource] -= qty

    # -----------------------------
    # Public Validator Method
    # -----------------------------
    def validate(self, task: str):
        """
        Validates AND reserves resources if available.
        """
        required = self._required_resources(task)

        missing_resources = {}

        for category in required:
            missing = self._check_category(
                required[category],
                self.available_resources[category],
            )
            if missing:
                missing_resources[category] = missing

        if missing_resources:
            return False, missing_resources

        # NEW: reserve resources after successful validation
        self._reserve_resources(required)

        return True, {}
