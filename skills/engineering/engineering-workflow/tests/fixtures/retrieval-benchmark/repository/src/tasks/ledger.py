class ExecutionLedger:
    def record_acceptance_evidence(self, task_id, evidence):
        """Attach verification evidence without changing canonical product truth."""
        return self.store.append(task_id, evidence)
