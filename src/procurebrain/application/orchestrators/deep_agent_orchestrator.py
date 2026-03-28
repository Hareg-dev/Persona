from dataclasses import dataclass


@dataclass(slots=True)
class DeepAgentTask:
    task_id: str
    title: str
    objective: str
    assigned_role: str


class DeepAgentOrchestrator:
    """
    Placeholder for future hierarchical or delegated agent execution.

    Normal agents handle one workflow directly.
    Deep agents split a large workflow into smaller coordinated sub-tasks.
    """

    def plan_subtasks(self, objective: str) -> list[DeepAgentTask]:
        return [
            DeepAgentTask(
                task_id="subtask-1",
                title="Initial decomposition",
                objective=objective,
                assigned_role="supervisor_node",
            )
        ]
