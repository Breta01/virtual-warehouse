"""Module loading agents' movement"""
import csv

from PySide2.QtCore import Property, QObject, QUrl, Signal, Slot


class Color:
    """Class calculating agent color."""

    def __init__(self, h, s, l, a):
        """Initialize with base HSLA color."""
        self._color = (h, s, l, a)

    def str(self):
        """Get color in hsla() formatted string."""
        h, s, l, a = self._color
        return f"hsla({h}, {s}%, {l}%, {a})"


class AgentManager(QObject):
    """Class controlling display and keyframing of picking agents."""

    agentsChanged = Signal()
    activeAgentsChanged = Signal()

    def __init__(self):
        """Initialize agent manager."""
        QObject.__init__(self)
        self.agents = {}
        self.keys = set()
        self._max_time = 0
        self._active = False

    @Property(int, constant=False, notify=agentsChanged)
    def max_time(self):
        """Get maximal time """
        return self._max_time

    @Property(bool, constant=False, notify=agentsChanged)
    def active(self):
        """Get true if agent visualization is active false otherwise."""
        return self._active

    @Property("QVariantList", constant=False, notify=agentsChanged)
    def agents_list(self):
        """Get description of agents for list visualization."""
        return self.keys

    @Slot(str)
    def toggle_agent(self, key):
        """Toggle agent from active agents set.

        Args:
            key (str): name/key of agent to toggle.
        """
        if key in self.keys:
            self.keys.remove(key)
        else:
            self.keys.add(key)

    @Slot(result="QVariantList")
    def get_colors(self):
        """Get list of colors for displaying agents."""
        return [self.agents[k]["color"].str() for k in sorted(self.keys)]

    @Slot(int, result="QVariantList")
    def get_timestep(self, time):
        """Get representation of positions for given time.

        Args:
            time (int): time of step (0 <= time <= max_time)

        Returns:
            list[list[int]]: list of agent steps
        """
        steps = []
        for k in sorted(self.keys):
            agent = self.agents[k]
            if agent["offset"] <= time < agent["offset"] + len(agent["steps"]):
                steps.append(agent["steps"][time - agent["offset"]])
            else:
                steps.append([-1, -1, 0, 0])
        return steps

    @Slot(QUrl)
    def load_data(self, file_path):
        """Load data picker agents data from provided CSV file.

        Args:
            file_path (QUrl): file path to CSV file
        """
        self.agents = {}
        with open(file_path.toLocalFile(), newline="") as csvfile:
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

        for i, k in enumerate(self.agents.keys()):
            self.agents[k]["color"] = Color(
                int(360 * i / len(self.agents)), 75, 70, 1.0
            )

        self._max_time = max(
            self.agents[a]["offset"] + len(self.agents[a]["steps"]) - 1
            for a in self.agents.keys()
        )
        self.keys = set(self.agents.keys())
        self._active = True
        self.agentsChanged.emit()
