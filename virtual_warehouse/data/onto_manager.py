"""Module managing working with ontology e.g. creating queries and classes."""
from subprocess import DEVNULL, check_call

import owlready2
from owlready2 import ConstrainedDatatype, sync_reasoner_pellet
from PySide2.QtCore import Property, QObject, Qt, QThread, Signal, Slot
from rdflib.plugins.sparql import prepareQuery

from virtual_warehouse.data.data_model import *  # skipcq: PYL-W0614


class OperationThread(QThread):
    """Thread which performs operations with ontology."""

    finished = Signal(object)

    def __init__(self, function):
        """Initialize thread params for loading file in separate thread.

        Args:
            function (function): function to be executed
        """
        super(OperationThread, self).__init__()
        self.function = function

    def run(self):
        """Load data from file path and emit data through signal."""
        data = self.function()
        self.finished.emit(data)


class OntoManager(QObject):
    """Class controlling ontology classes and reasoning."""

    classesChanged = Signal()
    queriesChanged = Signal()
    javaChanged = Signal()
    progressChanged = Signal()

    def __init__(self):
        """Initialize OntoController."""
        QObject.__init__(self)
        self._classes = {}
        self._queries = {}
        self._check_java()
        self._thread = None
        self._progress_value = 1

    @Property(float, constant=False, notify=progressChanged)
    def progress_value(self):
        """Get current progress value."""
        return self._progress_value

    @progress_value.setter
    def set_progress_value(self, val):
        """Set progress bar value."""
        self._progress_value = val
        self.progressChanged.emit()

    @Property(str, constant=False, notify=javaChanged)
    def java(self):  # skipcq: PYL-R0201
        """Get Java executable path for owlready reasoner."""
        return owlready2.JAVA_EXE

    @java.setter
    def set_java(self, val):
        """Set Java executable path for owlready reasoner."""
        owlready2.JAVA_EXE = val
        self._check_java()
        self.javaChanged.emit()

    @Property(bool, constant=False, notify=javaChanged)
    def java_correct(self):
        """Get true java path is correct."""
        return self._java_correct

    def _check_java(self):
        """Check if java path is set correctly."""
        try:
            check_call(
                [owlready2.JAVA_EXE, "--version"], stdout=DEVNULL, stderr=DEVNULL
            )
            self._java_correct = True
        except Exception:  # skipcq: PYL-W0703
            self._java_correct = False

    @Slot(str)
    def delete_class(self, cls):
        """Destroy given ontology class.

        Args:
            cls (str): name of new class for destruction
        """
        if cls in self._classes:
            destroy_entity(self._classes.pop(cls)[0])
            self.classesChanged.emit()

    def get_instances(self, is_class, name):
        """Get instances of custom class or query.

        Args:
            is_class (bool): True if class, False if query
            name (str): name of new classes

        Returns:
            list[Object]: list of class (RackLocation/Item/Order) instances
        """
        if is_class:
            return self._classes[name][0].instances()
        return self._queries[name][0]

    @Property("QVariantList", constant=False, notify=classesChanged)
    def classes(self):
        """Get list of classes for displaying in sideview."""
        return [
            {"name": k, "class": v[1], "count": len(v[0].instances())}
            for k, v in self._classes.items()
        ]

    @Slot(str, str, str, result=str)
    def check_create_class(self, name, cls, conditions):  # skipcq: PYL-R0201
        """Check if constuction parameters are correct.

        Args:
            name (str): name of new class
            cls (str): string describing class, possible values: "RackLocation", "Item", "Order"
            conditions (str): describing condition (later replace by more complex structure)
        """
        try:
            if len(name.strip()) > 0:
                return "Invalid name"
            if cls in ["RackLocation", "Item", "Order"]:
                return "Invalid class type"

            if len(conditions.strip()) != 0:
                full_condition = f"[{cls} & {conditions}]"
            else:
                full_condition = f"[{cls}]"
            # Test validity of conditions
            eval(full_condition)
            return None
        except Exception as e:  # skipcq: PYL-W0703
            return str(e)

    @Slot(str, str, str)
    def create_class(self, name, cls, conditions):
        """Construct new ontology class based on RackLocation, Item or Order.

        Args:
            name (str): name of new class
            cls (str): string describing class, possible values: "RackLocation", "Item", "Order"
            conditions (str): describing condition (later replace by more complex structure)
        """
        name = name.strip()
        if len(conditions.strip()) != 0:
            full_condition = f"[{cls} & {conditions}]"
        else:
            full_condition = f"[{cls}]"

        def creation():
            """Create new class."""
            with onto:
                new_class = type(
                    name, (eval(cls),), {"equivalent_to": eval(full_condition)}
                )
                sync_reasoner_pellet(debug=0, infer_property_values=False)
            return new_class

        def callback(new_class):
            """Save output of the thread."""
            self._classes[name] = (new_class, cls)
            self.classesChanged.emit()
            # self._thread = None
            self.progress_value = 1

        self.progress_value = 0
        self._thread = OperationThread(creation)
        self._thread.finished.connect(callback, Qt.QueuedConnection)
        self._thread.start()

    @staticmethod
    def _construct_query(cls, query):
        """Construct SPARQL query based on RackLocation, Item or Order."""
        i1 = "PREFIX : <http://warehouse/onto.owl>\n"
        i2 = "SELECT DISTINCT ?obj WHERE {\n"
        i3 = f"?obj a :{cls} . \n"
        return i1 + i2 + i3 + query + " }"

    @Slot(str, str, str, result=str)
    def check_create_query(self, name, cls, query):
        """Check correct query definition.

        Args:
            name (str): name of new query
            cls (str): string describing class, possible values: "RackLocation", "Item", "Order"
            query (str): describing SPARQL query (later replace by more complex structure)
        """
        self.progress_value = 0
        try:
            if len(name.strip()) > 0:
                return "Invalid name"
            if cls in ["RackLocation", "Item", "Order"]:
                return "Invalid class type"
            # Test validity of query
            prepareQuery(self._construct_query(cls, query))
            self.progress_value = 1
            return None
        except Exception as e:  # skipcq: PYL-W0703
            self.progress_value = 1
            return "Invalid query: " + str(e)

    @Slot(str, str, str)
    def create_query(self, name, cls, query):
        """Create new query and get instances.

        Args:
            name (str): name of new query
            cls (str): string describing class, possible values: "RackLocation", "Item", "Order"
            query (str): describing SPARQL query (later replace by more complex structure)
        """
        name = name.strip()
        q = self._construct_query(cls, query)

        print("---- QUERY ----")
        print(q)
        print("---- END QUERY ----")

        def creation():
            """Execute the query."""
            return list(default_world.sparql_query(q))

        def callback(instances):
            """Save output of the thread."""
            self._queries[name] = (instances, cls)
            self.queriesChanged.emit()
            # self._thread = None
            self.progress_value = 1

        self.progress_value = 0
        self._thread = OperationThread(creation)
        self._thread.finished.connect(callback, Qt.QueuedConnection)
        self._thread.start()

    @Slot(str)
    def delete_query(self, name):
        """Destroy given SPARQL query.

        Args:
            name (str): name of new query for destruction
        """
        if name in self._queries:
            del self._queries[name]
            self.queriesChanged.emit()

    @Property("QVariantList", constant=False, notify=queriesChanged)
    def queries(self):
        """Get list of queries for displaying in sideview."""
        return [
            {"name": k, "class": v[1], "count": len(v[0])}
            for k, v in self._queries.items()
        ]