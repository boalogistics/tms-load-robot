def login():
    pass

def run_lcr():
    pass

def book():
    pass

def dispatch():
    pass

class Truck:
    """
    Class to hold all information for the Married / Master truck.
    Object instance should be the truck number (truck1, truck2, etc.)
    """
    def __init__(self, married_load, carrier, dispatched):
        self.married_load = married_load
        self.carrier = carrier
        self.disaptched = dispatched

