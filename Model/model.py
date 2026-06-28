# Model/model.py v5

from mesa import Model
from mesa.time import RandomActivation

from Agents.manager_agent import ManagerAgent
from Agents.passenger_agent import PassengerAgent
from Agents.bus_agent import BusAgent
from Agents.ticketing_agent import TicketingAgent
from FIPA.acl import MessageTransportService

class BusStationModel(Model):
    """
    Multi-Agent Bus Ticketing Digitization System
    FIPA-Compliant with ACL Message Transport Service
    
    Simulates Kadawatha Highway Bus Depot (Sri Lankan Context)
    - Station Manager: Coordinates operations and manages physical ticketing
    - Ticketing System: Handles digital ticket processing
    - Buses: Transport passengers to various destinations
    - Passengers: Request tickets and travel
    - MTS: Routes FIPA ACL messages between agents
    """
    
    def __init__(self, num_passengers=10, num_buses=4, bus_routes=None):
        super().__init__()
        
        self.schedule = RandomActivation(self)
        
        # Initialize Message Transport Service
        self.mts = MessageTransportService(self)
        
        # Sri Lankan highway bus routes (Kadawatha depot)
        if bus_routes is None:
            self.available_routes = [
                'Moratuwa', 'Maharagama', 'Kottawa', 'Kaduwela',
                'Galle', 'Kandy', 'Matara', 'Mathugama'
            ]
        else:
            self.available_routes = bus_routes

        # --- 1. Create station manager ---
        self.station = ManagerAgent("StationManager", self)
        self.schedule.add(self.station)

        # --- 2. Create ticketing system ---
        self.ticketing_system = TicketingAgent("TicketingSystem", self)
        self.schedule.add(self.ticketing_system)

        # --- 3. Create buses with balanced route coverage ---
        self.buses = []
        for i in range(num_buses):
            bus = BusAgent(f"Bus {i+1}", self, capacity=33)  # Highway buses have larger capacity
            # Assign routes in round-robin to ensure coverage
            assigned_route = self.available_routes[i % len(self.available_routes)]
            bus.set_route(assigned_route)  # Set route and calculate travel time
            self.schedule.add(bus)
            self.buses.append(bus)

        # --- 4. Create passengers ---
        self.passengers = []
        for i in range(num_passengers):
            p = PassengerAgent(f"Passenger {i+1}", self, self.available_routes)
            self.schedule.add(p)
            self.passengers.append(p)

    def step(self):
        """Execute one step of the simulation"""
        self.schedule.step()
        
        # Deliver all queued FIPA messages
        self.mts.deliver_messages()