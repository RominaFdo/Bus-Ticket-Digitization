# Agents/passenger_agent.py v13 (v12 worked)

from mesa import Agent
import random
from FIPA.acl import FIPAAgent, ACLMessage, Performative, Protocol

class PassengerAgent(Agent, FIPAAgent):
    """
    Passenger Agent - Requests tickets and travels to destinations
    FIPA-Compliant with ACL messaging
    """
    def __init__(self, unique_id, model, available_routes):
        Agent.__init__(self, unique_id, model)
        FIPAAgent.__init__(self, unique_id)
        
        # Passenger attributes
        self.destination = random.choice(available_routes)
        self.state = 'arriving'  # arriving -> queued -> ticketed -> boarded -> traveling -> arrived
        self.ticket = None
        self.assigned_bus = None
        self.patience = random.randint(30, 45)  # Steps willing to wait (increased from 5-15 to 15-30)
        self.wait_time = 0
        
    def step(self):
        """Passenger's actions based on current state"""
        
        # Process incoming FIPA messages
        self.process_messages()
        
        if self.state == 'arriving':
            self.request_ticket()
            
        elif self.state == 'queued':
            self.wait_in_queue()
            
        elif self.state == 'ticketed':
            print(f"[{self.unique_id}] Waiting to board {self.assigned_bus.unique_id if self.assigned_bus else 'unknown bus'}...")
            
        elif self.state == 'boarded':
            print(f"[{self.unique_id}] On {self.assigned_bus.unique_id if self.assigned_bus else 'bus'}, traveling to {self.destination}")
            
        elif self.state == 'traveling':
            # Passenger is traveling with bus
            pass
            
        elif self.state == 'arrived':
            print(f"[{self.unique_id}] [+] Arrived at {self.destination}")
            self.complete_journey()
        
        # Clear processed messages
        self.clear_inbox()
    
    def process_messages(self):
        """Process incoming FIPA ACL messages"""
        messages = self.get_messages()
        
        for message in messages:
            if message.performative == Performative.AGREE:
                # Manager agreed to process ticket request
                self.handle_agree(message)
            
            elif message.performative == Performative.INFORM:
                # Ticket issued or other information
                self.handle_inform(message)
            
            elif message.performative == Performative.REFUSE:
                # Request refused
                self.handle_refuse(message)
            
            elif message.performative == Performative.REQUEST:
                # Request from bus to board
                if message.content.get('action') == 'board':
                    self.handle_board_request(message)
    
    def handle_agree(self, message: ACLMessage):
        """Handle AGREE message from manager"""
        position = message.content.get('position')
        print(f"[{self.unique_id}] [+] Request accepted, position in queue: {position}")
    
    def handle_inform(self, message: ACLMessage):
        """Handle INFORM messages"""
        content = message.content
        
        if content.get('action') == 'ticket_issued':
            ticket = content.get('ticket')
            self.receive_ticket(ticket)
    
    def handle_refuse(self, message: ACLMessage):
        """Handle REFUSE message"""
        reason = message.content.get('reason')
        print(f"[{self.unique_id}] [X] Request refused: {reason}")
    
    def handle_board_request(self, message: ACLMessage):
        """Handle boarding request from bus"""
        self.state = 'boarded'
        
        # Send confirmation immediately (no delay)
        confirm = ACLMessage(
            performative=Performative.CONFIRM,
            sender=self.unique_id,
            receiver=message.sender,
            content={'action': 'boarded'},
            protocol=Protocol.REQUEST,
            in_reply_to=message.reply_with
        )
        self.send_message(confirm)
        self.model.mts.route_message(confirm)
        
        # Immediately update state to traveling (skip waiting phase)
        if self.assigned_bus and self.assigned_bus.state == 'boarding':
            print(f"[{self.unique_id}] Boarded {message.sender} quickly")
    
    def request_ticket(self):
        """Request ticket from station manager using FIPA REQUEST"""
        print(f"[{self.unique_id}] Arriving at station, destination: {self.destination}")
        
        # Send REQUEST message to station manager
        message = ACLMessage(
            performative=Performative.REQUEST,
            sender=self.unique_id,
            receiver=self.model.station.unique_id,
            content={
                'action': 'request_ticket',
                'destination': self.destination
            },
            protocol=Protocol.REQUEST,
            reply_with=f"{self.unique_id}_req_{self.model.schedule.steps}"
        )
        
        self.send_message(message)
        self.model.mts.route_message(message)
        self.state = 'queued'
    
    def wait_in_queue(self):
        """Wait in queue and track patience"""
        self.wait_time += 1
        
        if self.wait_time >= self.patience:
            print(f"[{self.unique_id}] [!] Lost patience after waiting {self.wait_time} steps!")
            # Remove from queue and leave station
            if self in self.model.station.ticket_queue:
                self.model.station.ticket_queue.remove(self)
            self.state = 'left frustrated'
    
    def receive_ticket(self, ticket):
        """Receive ticket from manager"""
        self.ticket = ticket
        self.assigned_bus = None
        # Find the bus object
        for bus in self.model.buses:
            if bus.unique_id == ticket['bus_id']:
                self.assigned_bus = bus
                break
        
        self.state = 'ticketed'
        print(f"[{self.unique_id}] [TICKET] Received ticket! Seat {ticket['seat_number']} on {ticket['bus_id']}")
    
    def board_bus(self, bus):
        """Board assigned bus"""
        self.state = 'boarded'
        print(f"[{self.unique_id}] [BOARD] Boarded {bus.unique_id}")
    
    def start_travel(self):
        """Begin traveling"""
        self.state = 'traveling'
    
    def arrive_at_destination(self):
        """Arrive at destination"""
        self.state = 'arrived'
    
    def complete_journey(self):
        """Remove passenger from model after arrival"""
        # Remove from schedule
        self.model.schedule.remove(self)
        if self in self.model.passengers:
            self.model.passengers.remove(self)