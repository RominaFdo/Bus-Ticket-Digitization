# Agents/manager_agent.py v14 (v13 worked)

from mesa import Agent
import random
from FIPA.acl import FIPAAgent, ACLMessage, Performative, Protocol

class ManagerAgent(Agent, FIPAAgent):
    """
    Station Manager Agent - Coordinates bus operations and manages station resources
    FIPA-Compliant with ACL messaging
    """
    def __init__(self, unique_id, model):
        Agent.__init__(self, unique_id, model)
        FIPAAgent.__init__(self, unique_id)
        self.ticket_queue = []  # Queue of passengers waiting for tickets
        self.bus_schedule = {}  # Tracks bus departure times
        self.revenue = 0
        self.tickets_sold = 0
        
    def step(self):
        """Manager's actions each step"""
        print(f"\n[{self.unique_id}] === Station Status ===")
        print(f"Tickets sold today: {self.tickets_sold} | Revenue: LKR {self.revenue}")
        print(f"Queue length: {len(self.ticket_queue)}")
        
        # Process incoming FIPA messages
        self.process_messages()
        
        # Process ticket requests
        self.process_ticket_requests()
        
        # Manage bus departures
        self.coordinate_bus_departures()
        
        # Clear processed messages
        self.clear_inbox()
    
    def process_messages(self):
        """Process incoming FIPA ACL messages"""
        messages = self.get_messages()
        
        for message in messages:
            if message.performative == Performative.REQUEST:
                # Passenger requesting ticket
                if message.content.get('action') == 'request_ticket':
                    self.handle_ticket_request(message)
            
            elif message.performative == Performative.QUERY_IF:
                # Query about bus availability
                if message.content.get('query') == 'bus_available':
                    self.handle_availability_query(message)
            
            elif message.performative == Performative.INFORM:
                # Information from bus or ticketing system
                self.handle_inform(message)
    
    def handle_ticket_request(self, message: ACLMessage):
        """Handle ticket request from passenger"""
        passenger_id = message.sender
        destination = message.content.get('destination')
        
        # Find passenger agent
        passenger = None
        for p in self.model.passengers:
            if p.unique_id == passenger_id:
                passenger = p
                break
        
        if passenger and passenger not in self.ticket_queue:
            self.ticket_queue.append(passenger)
            
            # Send AGREE message
            response = ACLMessage(
                performative=Performative.AGREE,
                sender=self.unique_id,
                receiver=passenger_id,
                content={'message': 'Request accepted, added to queue', 'position': len(self.ticket_queue)},
                protocol=Protocol.REQUEST,
                in_reply_to=message.reply_with
            )
            self.send_message(response)
            self.model.mts.route_message(response)
    
    def handle_availability_query(self, message: ACLMessage):
        """Handle query about bus availability"""
        destination = message.content.get('destination')
        available_bus = self.find_available_bus(destination)
        
        response = ACLMessage(
            performative=Performative.INFORM if available_bus else Performative.DISCONFIRM,
            sender=self.unique_id,
            receiver=message.sender,
            content={
                'available': available_bus is not None,
                'bus_id': available_bus.unique_id if available_bus else None
            },
            protocol=Protocol.QUERY,
            in_reply_to=message.reply_with
        )
        self.send_message(response)
        self.model.mts.route_message(response)
        
    def add_to_queue(self, passenger):
        """Add passenger to ticketing queue"""
        if passenger not in self.ticket_queue:
            self.ticket_queue.append(passenger)
            print(f"[{self.unique_id}] Added {passenger.unique_id} to queue (position: {len(self.ticket_queue)})")
    
    def process_ticket_requests(self):
        """Process passengers in queue"""
        if not self.ticket_queue:
            return
            
        # Process up to 5 passengers per step (simulating multiple ticket counters)
        # Increased from 2 to 5 for faster boarding
        for _ in range(min(5, len(self.ticket_queue))):
            if self.ticket_queue:
                passenger = self.ticket_queue.pop(0)
                self.issue_ticket(passenger)
    
    def issue_ticket(self, passenger):
        """Issue ticket to passenger using FIPA protocol"""
        # Find available bus
        available_bus = self.find_available_bus(passenger.destination)
        
        if available_bus:
            ticket_price = self.calculate_price(passenger.destination)
            ticket = {
                'passenger_id': passenger.unique_id,
                'destination': passenger.destination,
                'bus_id': available_bus.unique_id,
                'price': ticket_price,
                'seat_number': len(available_bus.passengers) + 1
            }
            
            # Send INFORM message with ticket details
            message = ACLMessage(
                performative=Performative.INFORM,
                sender=self.unique_id,
                receiver=passenger.unique_id,
                content={
                    'action': 'ticket_issued',
                    'ticket': ticket
                },
                protocol=Protocol.REQUEST
            )
            self.send_message(message)
            self.model.mts.route_message(message)
            
            # Notify bus to board passenger
            board_message = ACLMessage(
                performative=Performative.REQUEST,
                sender=self.unique_id,
                receiver=available_bus.unique_id,
                content={
                    'action': 'board_passenger',
                    'passenger_id': passenger.unique_id
                },
                protocol=Protocol.REQUEST
            )
            self.send_message(board_message)
            self.model.mts.route_message(board_message)
            
            self.revenue += ticket_price
            self.tickets_sold += 1
            
            print(f"[{self.unique_id}] [+] Issued ticket to {passenger.unique_id}")
            print(f"   -> Bus: {available_bus.unique_id} | Seat: {ticket['seat_number']} | Price: LKR {ticket_price}")
        else:
            print(f"[{self.unique_id}] [X] No bus available for {passenger.unique_id} to {passenger.destination}")
            
            # Send REFUSE message
            refuse_message = ACLMessage(
                performative=Performative.REFUSE,
                sender=self.unique_id,
                receiver=passenger.unique_id,
                content={
                    'reason': 'No bus available for destination',
                    'destination': passenger.destination
                },
                protocol=Protocol.REQUEST
            )
            self.send_message(refuse_message)
            self.model.mts.route_message(refuse_message)
            
            # Re-add to queue
            self.ticket_queue.append(passenger)
    
    def find_available_bus(self, destination):
        """Find a bus that can accommodate passenger"""
        for bus in self.model.buses:
            if bus.can_board() and bus.route == destination:
                return bus
        return None
    
    def calculate_price(self, destination):
        """Calculate ticket price based on destination (LKR - Sri Lankan Rupees)"""
        price_map = {
            'Moratuwa': 320,
            'Maharagama': 200,
            'Kottawa': 150,
            'Kaduwela': 150,
            'Galle': 890,
            'Kandy': 640,
            'Matara': 1080,
            'Mathugama': 400
        }
        return price_map.get(destination, 200)
    
    def coordinate_bus_departures(self):
        """Signal buses when they should depart using FIPA messages"""
        for bus in self.model.buses:
            # Debug: Always log bus status
            if len(bus.passengers) > 0:
                print(f"[{self.unique_id}] Checking {bus.unique_id}: passengers={len(bus.passengers)}/{bus.capacity}, wait={bus.wait_time}/{bus.max_wait_time}, state={bus.state}")
            
            if bus.should_depart():
                print(f"[{self.unique_id}] [BUS] Signaling {bus.unique_id} to depart (passengers: {len(bus.passengers)}, wait: {bus.wait_time}/{bus.max_wait_time})")
                
                # Send REQUEST to depart
                depart_message = ACLMessage(
                    performative=Performative.REQUEST,
                    sender=self.unique_id,
                    receiver=bus.unique_id,
                    content={'action': 'depart'},
                    protocol=Protocol.REQUEST
                )
                self.send_message(depart_message)
                self.model.mts.route_message(depart_message)
    
    def handle_inform(self, message: ACLMessage):
        """Handle INFORM messages"""
        content = message.content
        if content.get('action') == 'bus_departed':
            print(f"[{self.unique_id}] Confirmed: {message.sender} has departed")
        elif content.get('action') == 'bus_arrived':
            print(f"[{self.unique_id}] Confirmed: {message.sender} arrived at destination")