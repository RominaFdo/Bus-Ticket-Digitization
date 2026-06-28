# # run.py

# from Model.model import BusStationModel

# # Create instance
# model = BusStationModel(num_passengers=5, num_buses=1)

# # Run for 10 steps
# for step in range(10):
#     print(f"--- Step {step} ---")
#     model.step()
# run.py

from Model.model import BusStationModel

def run_simulation(steps=20):
    """Run the bus ticketing simulation"""
    
    print("="*60)
    print("BUS TICKETING DIGITIZATION SYSTEM SIMULATION")
    print("="*60)
    print()
    
    # Create model with passengers and buses
    model = BusStationModel(num_passengers=5, num_buses=3)
    
    print(f"Simulation initialized:")
    print(f"  → Passengers: {len(model.passengers)}")
    print(f"  → Buses: {len(model.buses)}")
    print(f"  → Bus routes: {[bus.route for bus in model.buses]}")
    print(f"  → Passenger destinations: {[p.destination for p in model.passengers]}")
    print()
    print("="*60)
    print("STARTING SIMULATION")
    print("="*60)
    
    # Run simulation for specified steps
    for step in range(steps):
        print(f"\n{'='*60}")
        print(f"STEP {step + 1}/{steps}")
        print(f"{'='*60}")
        model.step()
    
    # Final report
    print("\n" + "="*60)
    print("FINAL SIMULATION REPORT")
    print("="*60)
    print(f"Total tickets sold: {model.station.tickets_sold}")
    print(f"Total revenue: ${model.station.revenue}")
    print(f"Remaining passengers: {len(model.passengers)}")
    print(f"Active buses: {len([b for b in model.buses if b.state != 'at_station'])}")
    
    print("\nBus status:")
    for bus in model.buses:
        print(f"  → {bus.unique_id}: {bus.state} - Route: {bus.route} - Passengers: {len(bus.passengers)}")
    
    print("\nPassenger status:")
    completed = sum(1 for p in model.passengers if p.state == 'arrived')
    traveling = sum(1 for p in model.passengers if p.state in ['traveling', 'boarded'])
    waiting = sum(1 for p in model.passengers if p.state in ['queued', 'ticketed'])
    
    print(f"  → Completed journey: {completed}")
    print(f"  → Currently traveling: {traveling}")
    print(f"  → Still waiting: {waiting}")
    
    print("\n" + "="*60)
    print("SIMULATION COMPLETE")
    print("="*60)

if __name__ == "__main__":
    # Run simulation for 30 steps
    run_simulation(steps=10)