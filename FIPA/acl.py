# FIPA/acl.py
"""
FIPA ACL (Agent Communication Language) Implementation
Supports standard FIPA performatives for agent communication
"""

from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional
import json

class Performative(Enum):
    """FIPA ACL Performatives"""
    # Core performatives
    REQUEST = "request"           # Request an action
    INFORM = "inform"             # Inform about facts
    QUERY_IF = "query-if"         # Query if something is true
    QUERY_REF = "query-ref"       # Query for reference
    CFP = "cfp"                   # Call for proposal
    PROPOSE = "propose"           # Propose a solution
    ACCEPT_PROPOSAL = "accept-proposal"
    REJECT_PROPOSAL = "reject-proposal"
    AGREE = "agree"               # Agree to perform action
    REFUSE = "refuse"             # Refuse to perform action
    FAILURE = "failure"           # Action failed
    CONFIRM = "confirm"           # Confirm truth of proposition
    DISCONFIRM = "disconfirm"     # Disconfirm truth
    NOT_UNDERSTOOD = "not-understood"
    SUBSCRIBE = "subscribe"       # Subscribe to information
    CANCEL = "cancel"             # Cancel previous request

class Protocol(Enum):
    """FIPA Interaction Protocols"""
    REQUEST = "fipa-request"
    QUERY = "fipa-query"
    CONTRACT_NET = "fipa-contract-net"
    PROPOSE = "fipa-propose"
    SUBSCRIBE = "fipa-subscribe"

@dataclass
class ACLMessage:
    """
    FIPA ACL Message Structure
    """
    performative: Performative
    sender: str
    receiver: str
    content: Any
    protocol: Optional[Protocol] = None
    conversation_id: Optional[str] = None
    reply_with: Optional[str] = None
    in_reply_to: Optional[str] = None
    language: str = "JSON"
    ontology: str = "bus-ticketing-ontology"
    
    def to_dict(self):
        """Convert message to dictionary"""
        return {
            'performative': self.performative.value,
            'sender': self.sender,
            'receiver': self.receiver,
            'content': self.content,
            'protocol': self.protocol.value if self.protocol else None,
            'conversation_id': self.conversation_id,
            'reply_with': self.reply_with,
            'in_reply_to': self.in_reply_to,
            'language': self.language,
            'ontology': self.ontology
        }
    
    def __repr__(self):
        return f"ACL({self.performative.value}: {self.sender} → {self.receiver})"

class MessageBox:
    """
    Message storage for agents (inbox/outbox)
    """
    def __init__(self):
        self.messages = []
    
    def add_message(self, message: ACLMessage):
        """Add message to box"""
        self.messages.append(message)
    
    def get_messages(self, performative: Optional[Performative] = None):
        """Get messages, optionally filtered by performative"""
        if performative:
            return [m for m in self.messages if m.performative == performative]
        return self.messages
    
    def clear(self):
        """Clear all messages"""
        self.messages.clear()
    
    def remove_message(self, message: ACLMessage):
        """Remove specific message"""
        if message in self.messages:
            self.messages.remove(message)

class FIPAAgent:
    """
    Base class for FIPA-compliant agents
    Provides message sending/receiving capabilities
    """
    def __init__(self, unique_id):
        self.unique_id = unique_id
        self.inbox = MessageBox()
        self.outbox = MessageBox()
    
    def send_message(self, message: ACLMessage):
        """Send ACL message"""
        self.outbox.add_message(message)
        # Log the message
        print(f"[{self.unique_id}] 📤 SEND: {message.performative.value} to {message.receiver}")
        print(f"         Content: {message.content}")
    
    def receive_message(self, message: ACLMessage):
        """Receive ACL message"""
        self.inbox.add_message(message)
        print(f"[{self.unique_id}] 📥 RECV: {message.performative.value} from {message.sender}")
        print(f"         Content: {message.content}")
    
    def get_messages(self, performative: Optional[Performative] = None):
        """Get received messages"""
        return self.inbox.get_messages(performative)
    
    def clear_inbox(self):
        """Clear inbox"""
        self.inbox.clear()
    
    def clear_outbox(self):
        """Clear outbox"""
        self.outbox.clear()

class MessageTransportService:
    """
    Message Transport Service (MTS)
    Routes messages between agents
    """
    def __init__(self, model):
        self.model = model
        self.message_queue = []
    
    def deliver_messages(self):
        """Deliver all queued messages to recipients"""
        while self.message_queue:
            message = self.message_queue.pop(0)
            recipient = self.find_agent(message.receiver)
            
            if recipient:
                recipient.receive_message(message)
            else:
                print(f"[MTS] ⚠️  Recipient not found: {message.receiver}")
    
    def find_agent(self, agent_id: str):
        """Find agent by ID in the model"""
        # Check station manager
        if self.model.station.unique_id == agent_id:
            return self.model.station
        
        # Check ticketing system
        if hasattr(self.model, 'ticketing_system') and self.model.ticketing_system.unique_id == agent_id:
            return self.model.ticketing_system
        
        # Check buses
        for bus in self.model.buses:
            if bus.unique_id == agent_id:
                return bus
        
        # Check passengers
        for passenger in self.model.passengers:
            if passenger.unique_id == agent_id:
                return passenger
        
        return None
    
    def route_message(self, message: ACLMessage):
        """Add message to delivery queue"""
        self.message_queue.append(message)