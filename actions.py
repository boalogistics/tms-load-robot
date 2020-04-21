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


class Truck:
    def __init__(self, truck_list):
        self.load_no = truck_list[0]
        self.married_load = truck_list[1]
        self.truck_no = truck_list[2]
        self.carrier_name = truck_list[3]
        self.dispatched = truck_list[4]
