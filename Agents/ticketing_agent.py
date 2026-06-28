# Agents/ticketing_agent.py v3
 
from mesa import Agent
from FIPA.acl import FIPAAgent, ACLMessage, Performative, Protocol

class TicketingAgent(Agent, FIPAAgent):
    """
    Ticketing Agent - Handles digital ticketing operations and validation
    FIPA-Compliant with ACL messaging
    """
    def __init__(self, unique_id, model):
        Agent.__init__(self, unique_id, model)
        FIPAAgent.__init__(self, unique_id)
        
        self.tickets_issued = []
        self.tickets_validated = []
        self.digital_queue = []  # Queue for online ticket requests
        self.system_status = 'online'
        
    def step(self):
        """Ticketing system's actions each step"""
        
        # Process incoming FIPA messages
        self.process_messages()
        
        # Process digital ticket requests
        self.process_digital_requests()
        
        # Generate analytics
        if self.model.schedule.steps % 10 == 0:  # Every 10 steps
            self.generate_report()
        
        # Clear processed messages
        self.clear_inbox()
    
    def process_messages(self):
        """Process incoming FIPA ACL messages"""
        messages = self.get_messages()
        
        for message in messages:
            if message.performative == Performative.REQUEST:
                action = message.content.get('action')
                
                if action == 'issue_digital_ticket':
                    self.handle_digital_ticket_request(message)
                elif action == 'validate_ticket':
                    self.handle_validation_request(message)
            
            elif message.performative == Performative.QUERY_IF:
                # Query about availability
                if message.content.get('query') == 'check_availability':
                    self.handle_availability_query(message)
            
            elif message.performative == Performative.SUBSCRIBE:
                # Subscribe to ticket updates
                print(f"[{self.unique_id}] {message.sender} subscribed to updates")
    
    def handle_digital_ticket_request(self, message: ACLMessage):
        """Handle digital ticket request"""
        passenger_id = message.sender
        destination = message.content.get('destination')
        
        # Check bus availability
        if self.check_availability(destination):
            ticket = self.issue_digital_ticket_internal(passenger_id, destination)
            
            # Send INFORM with ticket
            response = ACLMessage(
                performative=Performative.INFORM,
                sender=self.unique_id,
                receiver=passenger_id,
                content={
                    'action': 'digital_ticket_issued',
                    'ticket': ticket
                },
                protocol=Protocol.REQUEST,
                in_reply_to=message.reply_with
            )
            self.send_message(response)
            self.model.mts.route_message(response)
        else:
            # Send REFUSE
            refuse = ACLMessage(
                performative=Performative.REFUSE,
                sender=self.unique_id,
                receiver=passenger_id,
                content={'reason': 'No bus available for destination'},
                protocol=Protocol.REQUEST,
                in_reply_to=message.reply_with
            )
            self.send_message(refuse)
            self.model.mts.route_message(refuse)
    
    def handle_validation_request(self, message: ACLMessage):
        """Handle ticket validation request"""
        ticket_id = message.content.get('ticket_id')
        passenger_id = message.content.get('passenger_id')
        
        is_valid = self.validate_ticket(ticket_id, passenger_id)
        
        response = ACLMessage(
            performative=Performative.CONFIRM if is_valid else Performative.DISCONFIRM,
            sender=self.unique_id,
            receiver=message.sender,
            content={'valid': is_valid, 'ticket_id': ticket_id},
            protocol=Protocol.REQUEST,
            in_reply_to=message.reply_with
        )
        self.send_message(response)
        self.model.mts.route_message(response)
    
    def handle_availability_query(self, message: ACLMessage):
        """Handle availability query"""
        destination = message.content.get('destination')
        available = self.check_availability(destination)
        
        response = ACLMessage(
            performative=Performative.INFORM,
            sender=self.unique_id,
            receiver=message.sender,
            content={
                'destination': destination,
                'available': available,
                'next_bus': self.get_next_bus(destination)
            },
            protocol=Protocol.QUERY,
            in_reply_to=message.reply_with
        )
        self.send_message(response)
        self.model.mts.route_message(response)
    
    def issue_digital_ticket_internal(self, passenger_id, destination):
        """Internal method to issue digital ticket"""
        ticket = {
            'type': 'digital',
            'passenger_id': passenger_id,
            'destination': destination,
            'ticket_id': f"DT{len(self.tickets_issued) + 1:04d}",
            'status': 'issued',
            'timestamp': self.model.schedule.steps
        }
        self.tickets_issued.append(ticket)
        return ticket
    
    def add_digital_request(self, passenger, destination):
        """Add passenger to digital ticketing queue"""
        request = {
            'passenger': passenger,
            'destination': destination,
            'timestamp': self.model.schedule.steps
        }
        self.digital_queue.append(request)
        print(f"[{self.unique_id}] 📱 Digital ticket request from {passenger.unique_id}")
    
    def process_digital_requests(self):
        """Process digital ticket requests"""
        if not self.digital_queue:
            return
        
        # Process requests instantly (advantage of digital system)
        while self.digital_queue:
            request = self.digital_queue.pop(0)
            self.issue_digital_ticket(request['passenger'], request['destination'])
    
    def issue_digital_ticket(self, passenger, destination):
        """Issue digital ticket"""
        ticket = {
            'type': 'digital',
            'passenger_id': passenger.unique_id,
            'destination': destination,
            'ticket_id': f"DT{len(self.tickets_issued) + 1:04d}",
            'status': 'issued',
            'timestamp': self.model.schedule.steps
        }
        
        self.tickets_issued.append(ticket)
        print(f"[{self.unique_id}] ✓ Digital ticket {ticket['ticket_id']} issued to {passenger.unique_id}")
        
        return ticket
    
    def validate_ticket(self, ticket_id, passenger_id):
        """Validate ticket during boarding"""
        for ticket in self.tickets_issued:
            if ticket['ticket_id'] == ticket_id and ticket['passenger_id'] == passenger_id:
                if ticket['status'] == 'issued':
                    ticket['status'] = 'validated'
                    self.tickets_validated.append(ticket)
                    print(f"[{self.unique_id}] ✓ Ticket {ticket_id} validated for {passenger_id}")
                    return True
                else:
                    print(f"[{self.unique_id}] ✗ Ticket {ticket_id} already used")
                    return False
        
        print(f"[{self.unique_id}] ✗ Invalid ticket {ticket_id}")
        return False
    
    def generate_report(self):
        """Generate ticketing analytics report"""
        print(f"\n[{self.unique_id}] === TICKETING SYSTEM REPORT ===")
        print(f"Total tickets issued: {len(self.tickets_issued)}")
        print(f"Tickets validated: {len(self.tickets_validated)}")
        print(f"Digital queue length: {len(self.digital_queue)}")
        print(f"System status: {self.system_status}")
        
        # Destination breakdown
        destinations = {}
        for ticket in self.tickets_issued:
            dest = ticket['destination']
            destinations[dest] = destinations.get(dest, 0) + 1
        
        print("Tickets by destination:")
        for dest, count in destinations.items():
            print(f"  → {dest}: {count}")
    
    def check_availability(self, destination):
        """Check bus availability for destination"""
        for bus in self.model.buses:
            if bus.route == destination and bus.can_board():
                return True
        return False
    
    def get_next_bus(self, destination):
        """Get next available bus for destination"""
        for bus in self.model.buses:
            if bus.route == destination and bus.can_board():
                return bus.unique_id
        return None