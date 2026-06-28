# Agents/bus_agent.py v22 (v20 worked)

def set_route(self, route):
        """Set route and calculate travel time based on distance"""
        self.route = route
        travel_times = {
            'Moratuwa': random.randint(18, 25),      # ~25 km - medium distance
            'Maharagama': random.randint(12, 18),    # ~15 km - short distance
            'Kottawa': random.randint(10, 15),       # ~12 km - short distance
            'Kaduwela': random.randint(14, 20),      # ~18 km - short-medium distance
            'Galle': random.randint(35, 45),         # ~115 km - long distance
            'Kandy': random.randint(32, 42),         # ~110 km - long distance
            'Matara': random.randint(45, 55),        # ~160 km - very long distance
            'Mathugama': random.randint(22, 30)      # ~60 km - medium distance
        }
        self.max_travel_time = travel_times.get(route, random.randint(15, 25))
        print(f"[{self.unique_id}] Route set to {route} - Travel time: {self.max_travel_time} steps")# Agents/bus_agent.py

from mesa import Agent
import random
from FIPA.acl import FIPAAgent, ACLMessage, Performative, Protocol

class BusAgent(Agent, FIPAAgent):
    """
    Bus Agent - Transports passengers to destinations
    FIPA-Compliant with ACL messaging
    """
    def __init__(self, unique_id, model, capacity=5):
        Agent.__init__(self, unique_id, model)
        FIPAAgent.__init__(self, unique_id)
        
        self.capacity = capacity
        self.passengers = []
        self.route = None  # Will be assigned by model
        self.state = 'at_station'  # at_station -> boarding -> departed -> traveling -> arrived
        self.travel_time = 0
        self.max_travel_time = 0  # Will be set based on route
        self.wait_time = 0
        self.max_wait_time = 20  # Wait up to 20 steps before departing (increased from 5)
        
    def step(self):
        """Bus actions based on current state"""
        
        # Process incoming FIPA messages first
        self.process_messages()
        
        if self.state == 'at_station':
            self.wait_at_station()
            
        elif self.state == 'boarding':
            # Continue incrementing wait time while boarding
            if len(self.passengers) > 0:
                self.wait_time += 1
            print(f"[{self.unique_id}] Boarding passengers ({len(self.passengers)}/{self.capacity}) - Wait: {self.wait_time}/{self.max_wait_time}")
            
        elif self.state == 'departed':
            self.start_journey()
            
        elif self.state == 'traveling':
            self.travel()
            
        elif self.state == 'arrived':
            self.unload_passengers()
            self.return_to_station()
        
        # Clear processed messages
        self.clear_inbox()
    
    def process_messages(self):
        """Process incoming FIPA ACL messages"""
        messages = self.get_messages()
        
        for message in messages:
            if message.performative == Performative.REQUEST:
                action = message.content.get('action')
                
                if action == 'board_passenger':
                    self.handle_board_request(message)
                elif action == 'depart':
                    self.handle_depart_request(message)
            
            elif message.performative == Performative.QUERY_IF:
                # Query about capacity or availability
                self.handle_query(message)
            
            elif message.performative == Performative.CONFIRM:
                # Passenger confirmed boarding
                self.handle_confirm(message)
    
    def handle_board_request(self, message: ACLMessage):
        """Handle request from manager to board a passenger"""
        passenger_id = message.content.get('passenger_id')
        
        # Find passenger
        passenger = None
        for p in self.model.passengers:
            if p.unique_id == passenger_id:
                passenger = p
                break
        
        if passenger and self.can_board():
            self.passengers.append(passenger)
            passenger.assigned_bus = self
            self.state = 'boarding'
            
            # Send REQUEST to passenger to board
            board_msg = ACLMessage(
                performative=Performative.REQUEST,
                sender=self.unique_id,
                receiver=passenger_id,
                content={'action': 'board'},
                protocol=Protocol.REQUEST,
                reply_with=f"{self.unique_id}_board_{self.model.schedule.steps}"
            )
            self.send_message(board_msg)
            self.model.mts.route_message(board_msg)
            
            # Send INFORM back to manager (less verbose logging)
            response = ACLMessage(
                performative=Performative.INFORM,
                sender=self.unique_id,
                receiver=message.sender,
                content={'action': 'passenger_boarded', 'passenger_id': passenger_id},
                protocol=Protocol.REQUEST,
                in_reply_to=message.reply_with
            )
            self.send_message(response)
            self.model.mts.route_message(response)
            
            # Simplified logging (no individual passenger boarding messages)
            if len(self.passengers) % 5 == 0 or len(self.passengers) == 1:
                print(f"[{self.unique_id}] Boarding progress: {len(self.passengers)}/{self.capacity}")
        else:
            # Send REFUSE
            refuse = ACLMessage(
                performative=Performative.REFUSE,
                sender=self.unique_id,
                receiver=message.sender,
                content={'reason': 'Bus full or unavailable'},
                protocol=Protocol.REQUEST,
                in_reply_to=message.reply_with
            )
            self.send_message(refuse)
            self.model.mts.route_message(refuse)
    
    def handle_depart_request(self, message: ACLMessage):
        """Handle depart request from manager"""
        print(f"[{self.unique_id}] Received DEPART request from {message.sender}")
        
        if len(self.passengers) > 0:
            print(f"[{self.unique_id}] [DEPART] Departing with {len(self.passengers)} passengers!")
            self.depart()
            
            # Send INFORM confirmation
            response = ACLMessage(
                performative=Performative.INFORM,
                sender=self.unique_id,
                receiver=message.sender,
                content={'action': 'bus_departed', 'passenger_count': len(self.passengers)},
                protocol=Protocol.REQUEST,
                in_reply_to=message.reply_with
            )
            self.send_message(response)
            self.model.mts.route_message(response)
        else:
            print(f"[{self.unique_id}] Cannot depart - no passengers")
            # Send REFUSE
            refuse = ACLMessage(
                performative=Performative.REFUSE,
                sender=self.unique_id,
                receiver=message.sender,
                content={'reason': 'No passengers to transport'},
                protocol=Protocol.REQUEST,
                in_reply_to=message.reply_with
            )
            self.send_message(refuse)
            self.model.mts.route_message(refuse)
    
    def handle_query(self, message: ACLMessage):
        """Handle queries about bus status"""
        response = ACLMessage(
            performative=Performative.INFORM,
            sender=self.unique_id,
            receiver=message.sender,
            content={
                'can_board': self.can_board(),
                'capacity': self.capacity,
                'current_passengers': len(self.passengers),
                'route': self.route,
                'state': self.state
            },
            protocol=Protocol.QUERY,
            in_reply_to=message.reply_with
        )
        self.send_message(response)
        self.model.mts.route_message(response)
    
    def handle_confirm(self, message: ACLMessage):
        """Handle confirmation from passenger"""
        if message.content.get('action') == 'boarded':
            print(f"[{self.unique_id}] [+] {message.sender} confirmed boarding")
    
    def can_board(self):
        """Check if bus can accept more passengers"""
        return len(self.passengers) < self.capacity and self.state in ['at_station', 'boarding']
    
    def set_route(self, route):
        """Set route and calculate travel time based on distance"""
        self.route = route
        # Travel times based on approximate distances (in simulation steps)
        # Closer destinations = fewer steps, farther = more steps
        travel_times = {
            'Moratuwa': random.randint(18, 25),      # ~25 km - medium distance
            'Maharagama': random.randint(12, 18),    # ~15 km - short distance
            'Kottawa': random.randint(10, 15),       # ~12 km - short distance
            'Kaduwela': random.randint(14, 20),      # ~18 km - short-medium distance
            'Galle': random.randint(35, 45),         # ~115 km - long distance
            'Kandy': random.randint(32, 42),         # ~110 km - long distance
            'Matara': random.randint(45, 55),        # ~160 km - very long distance
            'Mathugama': random.randint(22, 30)      # ~60 km - medium distance
        }
        self.max_travel_time = travel_times.get(route, random.randint(15, 25))
        print(f"[{self.unique_id}] Route set to {route} - Travel time: {self.max_travel_time} steps")
    
    def board_passenger(self, passenger):
        """Board a passenger onto the bus"""
        if self.can_board():
            self.passengers.append(passenger)
            passenger.board_bus(self)
            self.state = 'boarding'
            print(f"[{self.unique_id}] {passenger.unique_id} boarded ({len(self.passengers)}/{self.capacity})")
            return True
        return False
    
    def wait_at_station(self):
        """Wait at station for passengers"""
        if len(self.passengers) > 0:
            self.wait_time += 1
            print(f"[{self.unique_id}] Waiting at station ({self.wait_time}/{self.max_wait_time}) - {len(self.passengers)} passengers")
        elif len(self.passengers) == 0:
            # Reset wait time if no passengers
            self.wait_time = 0
    
    def should_depart(self):
        """Determine if bus should depart"""
        # Depart if full or waited long enough with at least one passenger
        is_full = len(self.passengers) >= self.capacity
        waited_enough = self.wait_time >= self.max_wait_time and len(self.passengers) > 0
        
        return (is_full or waited_enough) and self.state in ['at_station', 'boarding']
    
    def depart(self):
        """Depart from station"""
        if len(self.passengers) > 0:
            self.state = 'departed'
            print(f"[{self.unique_id}] [BUS] DEPARTING with {len(self.passengers)} passengers to {self.route}")
        else:
            print(f"[{self.unique_id}] Cannot depart - no passengers")
    
    def start_journey(self):
        """Begin journey"""
        self.state = 'traveling'
        for passenger in self.passengers:
            passenger.start_travel()
    
    def travel(self):
        """Travel towards destination"""
        self.travel_time += 1
        progress = int((self.travel_time / self.max_travel_time) * 100)
        print(f"[{self.unique_id}] [TRAVEL] Traveling to {self.route}... {progress}% complete")
        
        if self.travel_time >= self.max_travel_time:
            self.state = 'arrived'
    
    def unload_passengers(self):
        """Unload passengers at destination with FIPA messages"""
        print(f"[{self.unique_id}] [ARRIVED] ARRIVED at {self.route}! Unloading {len(self.passengers)} passengers")
        
        # Inform manager of arrival
        arrival_msg = ACLMessage(
            performative=Performative.INFORM,
            sender=self.unique_id,
            receiver=self.model.station.unique_id,
            content={'action': 'bus_arrived', 'route': self.route, 'passenger_count': len(self.passengers)},
            protocol=Protocol.REQUEST
        )
        self.send_message(arrival_msg)
        self.model.mts.route_message(arrival_msg)
        
        for passenger in self.passengers:
            passenger.arrive_at_destination()
            print(f"   -> {passenger.unique_id} has disembarked")
        
        self.passengers.clear()
    
    def return_to_station(self):
        """Return to station and reset for next trip"""
        print(f"[{self.unique_id}] [RETURN] Returning to station...")
        self.state = 'at_station'
        self.travel_time = 0
        self.wait_time = 0
        # Keep the same route and travel time (highway buses maintain routes)
        print(f"[{self.unique_id}] Ready for next trip to {self.route} (travel time: {self.max_travel_time} steps)")