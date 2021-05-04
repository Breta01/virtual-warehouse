"""Module loading agents' movement"""
import csv

from PySide2.QtCore import Property, QObject, Signal, Slot


class AgentManager(QObject):
    """Class controlling display and keyframing of picking agents."""

    agentsChanged = Signal()

    def __init__(self):
        """Initialize agent manager."""
        QObject.__init__(self)
        self.agents = {}
        self.keys = []
        self._max_time = 0

    @Property(int, constant=False, notify=agentsChanged)
    def num_agents(self):
        """Get number of agents (property)."""
        return len(self.keys)

    @Property(int, constant=False, notify=agentsChanged)
    def max_time(self):
        """Get maximal time """
        return self._max_time

    @Slot(int, result="QVariantList")
    def get_timestep(self, time):
        """Get representation of positions for given time.

        Args:
            time (int): time of step (0 <= time <= max_time)

        Returns:
            list[list]: list of agent steps
        """
        steps = []
        for k in self.keys:
            agent = self.agents[k]
            if agent["offset"] <= time < agent["offset"] + len(agent["steps"]):
                steps.append(agent["steps"][time - agent["offset"]])
            else:
                steps.append([-1, -1, 0, 0])
        return steps

    def load_data(self, file_path):
        """Load data picker agents data from provided CSV file.

        Args:
            file_path (str): file path to CSV file
        """
        self.agents = {}
        with open(file_path, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for r in reader:
                agent = r["agent"]
                if agent not in self.agents:
                    self.agents[agent] = {
                        "offset": int(r["time"]),
                        "steps": [
                            list(
                                map(
                                    int,
                                    (r["locX"], r["locY"], r["isPick"], r["orderId"]),
                                )
                            )
                        ],
                    }
                else:
                    time_diff = int(r["time"]) - (
                        self.agents[agent]["offset"] + len(self.agents[agent]["steps"])
                    )
                    if time_diff > 0:
                        self.agents[agent]["steps"].extend(
                            time_diff * [self.agents[agent]["steps"][-1]]
                        )
                    self.agents[agent]["steps"].append(
                        list(
                            map(int, (r["locX"], r["locY"], r["isPick"], r["orderId"]))
                        )
                    )

        self.keys = sorted(list(self.agents.keys()))
        self._max_time = max(
            self.agents[a]["offset"] + len(self.agents[a]["steps"]) - 1
            for a in self.keys
        )
        self.agentsChanged.emit()
