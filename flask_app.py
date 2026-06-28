# # flask_app.py v2

# from flask import Flask, render_template_string, jsonify, request
# from Model.model import BusStationModel
# import threading
# import time

# app = Flask(__name__)

# # Global model instance
# model = None
# simulation_running = False
# simulation_thread = None

# HTML_TEMPLATE = """
# <!DOCTYPE html>
# <html>
# <head>
#     <title>Kadawatha Highway Bus Depot - Live Multi Agent System Dashboard</title>
#     <style>
#         body {
#             font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#             margin: 0;
#             padding: 20px;
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             color: #333;
#         }
#         .container {
#             max-width: 1400px;
#             margin: 0 auto;
#         }
#         .header {
#             background: white;
#             padding: 20px;
#             border-radius: 10px;
#             box-shadow: 0 4px 6px rgba(0,0,0,0.1);
#             margin-bottom: 20px;
#             text-align: center;
#         }
#         h1 {
#             margin: 0;
#             color: #667eea;
#         }
#         .setup-section {
#             background: white;
#             padding: 20px;
#             border-radius: 10px;
#             margin-bottom: 20px;
#             box-shadow: 0 4px 6px rgba(0,0,0,0.1);
#         }
#         .setup-section h3 {
#             margin-top: 0;
#             color: #667eea;
#         }
#         .form-group {
#             margin-bottom: 15px;
#         }
#         label {
#             display: block;
#             font-weight: 600;
#             margin-bottom: 5px;
#         }
#         input[type="number"], select {
#             width: 200px;
#             padding: 8px;
#             border: 2px solid #ddd;
#             border-radius: 5px;
#             font-size: 14px;
#         }
#         .controls {
#             display: flex;
#             gap: 10px;
#             justify-content: center;
#             margin-top: 15px;
#             flex-wrap: wrap;
#         }
#         button {
#             padding: 10px 20px;
#             border: none;
#             border-radius: 5px;
#             cursor: pointer;
#             font-size: 16px;
#             transition: all 0.3s;
#         }
#         .btn-start {
#             background: #10b981;
#             color: white;
#         }
#         .btn-stop {
#             background: #ef4444;
#             color: white;
#         }
#         .btn-reset {
#             background: #6366f1;
#             color: white;
#         }
#         .btn-step {
#             background: #f59e0b;
#             color: white;
#         }
#         .btn-create {
#             background: #8b5cf6;
#             color: white;
#         }
#         button:hover {
#             transform: translateY(-2px);
#             box-shadow: 0 4px 8px rgba(0,0,0,0.2);
#         }
#         button:disabled {
#             background: #ccc;
#             cursor: not-allowed;
#         }
#         .grid {
#             display: grid;
#             grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
#             gap: 20px;
#             margin-top: 20px;
#         }
#         .card {
#             background: white;
#             padding: 20px;
#             border-radius: 10px;
#             box-shadow: 0 4px 6px rgba(0,0,0,0.1);
#         }
#         .card h2 {
#             margin-top: 0;
#             color: #667eea;
#             border-bottom: 2px solid #667eea;
#             padding-bottom: 10px;
#         }
#         .stat {
#             display: flex;
#             justify-content: space-between;
#             padding: 8px 0;
#             border-bottom: 1px solid #eee;
#         }
#         .stat:last-child {
#             border-bottom: none;
#         }
#         .stat-label {
#             font-weight: 600;
#         }
#         .stat-value {
#             color: #667eea;
#             font-weight: bold;
#         }
#         .bus-item, .passenger-item {
#             background: #f8fafc;
#             padding: 10px;
#             margin: 8px 0;
#             border-radius: 5px;
#             border-left: 4px solid #667eea;
#         }
#         .status {
#             display: inline-block;
#             padding: 3px 8px;
#             border-radius: 3px;
#             font-size: 12px;
#             font-weight: 600;
#         }
#         .status-active { background: #10b981; color: white; }
#         .status-waiting { background: #f59e0b; color: white; }
#         .status-arrived { background: #6366f1; color: white; }
#         .status-traveling { background: #8b5cf6; color: white; }
#         .status-boarding { background: #3b82f6; color: white; }
#         .status-at_station { background: #6b7280; color: white; }
#     </style>
# </head>
# <body>
#     <div class="container">
#         <div class="header">
#             <h1>Kadawatha Highway Bus Depot</h1>
#             <p>Live Multi-Agent System Dashboard</p>
#         </div>

#         <div class="setup-section">
#             <h3>Simulation Setup</h3>
#             <div class="form-group">
#                 <label for="num_passengers">Number of Passengers:</label>
#                 <input type="number" id="num_passengers" value="10" min="1" max="100">
#             </div>
#             <div class="form-group">
#                 <label for="num_buses">Number of Buses:</label>
#                 <input type="number" id="num_buses" value="4" min="1" max="20">
#             </div>
#             <div class="controls">
#                 <button class="btn-create" onclick="createSimulation()">Create New Simulation</button>
#                 <button class="btn-start" onclick="startSimulation()">Auto Run</button>
#                 <button class="btn-step" onclick="stepSimulation()">Step Once</button>
#                 <button class="btn-stop" onclick="stopSimulation()">Stop</button>
#                 <button class="btn-reset" onclick="resetSimulation()">Reset</button>
#             </div>
#         </div>

#         <div class="grid">
#             <div class="card">
#                 <h2>Station Overview</h2>
#                 <div class="stat">
#                     <span class="stat-label">Tickets Sold:</span>
#                     <span class="stat-value" id="tickets-sold">0</span>
#                 </div>
#                 <div class="stat">
#                     <span class="stat-label">Revenue:</span>
#                     <span class="stat-value" id="revenue">LKR 0</span>
#                 </div>
#                 <div class="stat">
#                     <span class="stat-label">Queue Length:</span>
#                     <span class="stat-value" id="queue-length">0</span>
#                 </div>
#                 <div class="stat">
#                     <span class="stat-label">Current Step:</span>
#                     <span class="stat-value" id="current-step">0</span>
#                 </div>
#                 <div class="stat">
#                     <span class="stat-label">Status:</span>
#                     <span class="stat-value" id="sim-status">Not Started</span>
#                 </div>
#             </div>

#             <div class="card">
#                 <h2>Active Buses</h2>
#                 <div id="buses-list"></div>
#             </div>

#             <div class="card">
#                 <h2>Passengers</h2>
#                 <div id="passengers-list"></div>
#             </div>
#         </div>
#     </div>

#     <script>
#         let updateInterval;

#         function createSimulation() {
#             const numPassengers = document.getElementById('num_passengers').value;
#             const numBuses = document.getElementById('num_buses').value;
            
#             fetch('/create', {
#                 method: 'POST',
#                 headers: {'Content-Type': 'application/json'},
#                 body: JSON.stringify({
#                     num_passengers: parseInt(numPassengers),
#                     num_buses: parseInt(numBuses)
#                 })
#             })
#             .then(response => response.json())
#             .then(data => {
#                 console.log(data.message);
#                 updateDashboard();
#             });
#         }

#         function startSimulation() {
#             fetch('/start', {method: 'POST'})
#                 .then(response => response.json())
#                 .then(data => {
#                     console.log(data.message);
#                     if (!updateInterval) {
#                         updateInterval = setInterval(updateDashboard, 1000);
#                     }
#                 });
#         }

#         function stepSimulation() {
#             fetch('/step', {method: 'POST'})
#                 .then(response => response.json())
#                 .then(data => {
#                     console.log(data.message);
#                     updateDashboard();
#                 });
#         }

#         function stopSimulation() {
#             fetch('/stop', {method: 'POST'})
#                 .then(response => response.json())
#                 .then(data => {
#                     console.log(data.message);
#                     if (updateInterval) {
#                         clearInterval(updateInterval);
#                         updateInterval = null;
#                     }
#                 });
#         }

#         function resetSimulation() {
#             fetch('/reset', {method: 'POST'})
#                 .then(response => response.json())
#                 .then(data => {
#                     console.log(data.message);
#                     if (updateInterval) {
#                         clearInterval(updateInterval);
#                         updateInterval = null;
#                     }
#                     updateDashboard();
#                 });
#         }

#         function updateDashboard() {
#             fetch('/status')
#                 .then(response => response.json())
#                 .then(data => {
#                     // Update stats
#                     document.getElementById('tickets-sold').textContent = data.tickets_sold;
#                     document.getElementById('revenue').textContent = 'LKR ' + data.revenue;
#                     document.getElementById('queue-length').textContent = data.queue_length;
#                     document.getElementById('current-step').textContent = data.current_step;
#                     document.getElementById('sim-status').textContent = data.running ? 'Running' : 'Stopped';

#                     // Update buses
#                     const busesList = document.getElementById('buses-list');
#                     busesList.innerHTML = data.buses.map(bus => `
#                         <div class="bus-item">
#                             <strong>${bus.id}</strong> to ${bus.route}<br>
#                             <span class="status status-${bus.state.replace(' ', '_')}">${bus.state}</span>
#                             Passengers: ${bus.passengers}/${bus.capacity}
#                         </div>
#                     `).join('');

#                     // Update passengers
#                     const passengersList = document.getElementById('passengers-list');
#                     const displayPassengers = data.passengers.slice(0, 15);
#                     passengersList.innerHTML = displayPassengers.map(p => `
#                         <div class="passenger-item">
#                             <strong>${p.id}</strong> to ${p.destination}<br>
#                             <span class="status status-${p.state.replace(' ', '_')}">${p.state}</span>
#                         </div>
#                     `).join('');
                    
#                     if (data.passengers.length > 15) {
#                         passengersList.innerHTML += `<p>... and ${data.passengers.length - 15} more passengers</p>`;
#                     }
#                 });
#         }

#         // Initial load
#         updateDashboard();
#     </script>
# </body>
# </html>
# """

# def run_simulation():
#     """Run simulation in background thread"""
#     global simulation_running, model
#     while simulation_running:
#         if model:
#             model.step()
#         time.sleep(1)  # 1 step per second

# @app.route('/')
# def index():
#     return render_template_string(HTML_TEMPLATE)

# @app.route('/create', methods=['POST'])
# def create():
#     global model, simulation_running
#     simulation_running = False
#     time.sleep(0.5)
    
#     data = request.get_json()
#     num_passengers = data.get('num_passengers', 10)
#     num_buses = data.get('num_buses', 4)
    
#     model = BusStationModel(num_passengers=num_passengers, num_buses=num_buses)
#     return jsonify({'message': f'Simulation created with {num_passengers} passengers and {num_buses} buses'})

# @app.route('/start', methods=['POST'])
# def start():
#     global simulation_running, simulation_thread, model
    
#     if not model:
#         model = BusStationModel(num_passengers=10, num_buses=4)
    
#     if not simulation_running:
#         simulation_running = True
#         simulation_thread = threading.Thread(target=run_simulation, daemon=True)
#         simulation_thread.start()
#         return jsonify({'message': 'Simulation started (auto-running)'})
#     return jsonify({'message': 'Simulation already running'})

# @app.route('/step', methods=['POST'])
# def step():
#     global model
#     if not model:
#         model = BusStationModel(num_passengers=10, num_buses=4)
    
#     model.step()
#     return jsonify({'message': 'Stepped once'})

# @app.route('/stop', methods=['POST'])
# def stop():
#     global simulation_running
#     simulation_running = False
#     return jsonify({'message': 'Simulation stopped'})

# @app.route('/reset', methods=['POST'])
# def reset():
#     global model, simulation_running
#     simulation_running = False
#     time.sleep(0.5)
#     model = BusStationModel(num_passengers=10, num_buses=4)
#     return jsonify({'message': 'Simulation reset'})

# @app.route('/status')
# def status():
#     global simulation_running
#     if not model:
#         return jsonify({
#             'tickets_sold': 0,
#             'revenue': 0,
#             'queue_length': 0,
#             'current_step': 0,
#             'running': False,
#             'buses': [],
#             'passengers': []
#         })
    
#     return jsonify({
#         'tickets_sold': model.station.tickets_sold,
#         'revenue': model.station.revenue,
#         'queue_length': len(model.station.ticket_queue),
#         'current_step': model.schedule.steps,
#         'running': simulation_running,
#         'buses': [{
#             'id': bus.unique_id,
#             'route': bus.route,
#             'state': bus.state,
#             'passengers': len(bus.passengers),
#             'capacity': bus.capacity
#         } for bus in model.buses],
#         'passengers': [{
#             'id': p.unique_id,
#             'destination': p.destination,
#             'state': p.state
#         } for p in model.passengers]
#     })

# if __name__ == '__main__':
#     print("Starting Kadawatha Highway Bus Depot Dashboard...")
#     print("Visit: http://localhost:5000")
#     app.run(debug=True, use_reloader=False)

# flask_app.py

from flask import Flask, render_template_string, jsonify, request
from Model.model import BusStationModel
import threading
import time

app = Flask(__name__)

# Global model instance
model = None
simulation_running = False
simulation_thread = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Kadawatha Highway Bus Depot - Management System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8fafc;
            color: #1e293b;
            line-height: 1.6;
        }
        
        /* Header */
        .header {
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
            color: white;
            padding: 1.5rem 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 0.25rem;
        }
        
        .header p {
            font-size: 0.875rem;
            opacity: 0.9;
        }
        
        /* Layout */
        .container {
            display: flex;
            height: calc(100vh - 88px);
        }
        
        /* Sidebar */
        .sidebar {
            width: 280px;
            background: white;
            border-right: 1px solid #e2e8f0;
            overflow-y: auto;
            transition: margin-left 0.3s;
        }
        
        .sidebar.hidden {
            margin-left: -280px;
        }
        
        .sidebar-section {
            padding: 1.5rem;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .sidebar-section h3 {
            font-size: 0.875rem;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 1rem;
        }
        
        /* Main Content */
        .main-content {
            flex: 1;
            overflow-y: auto;
            padding: 2rem;
        }
        
        /* Toolbar */
        .toolbar {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .toolbar-left {
            display: flex;
            gap: 0.5rem;
            align-items: center;
        }
        
        .toolbar-right {
            display: flex;
            gap: 0.75rem;
        }
        
        /* Buttons */
        button {
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 6px;
            font-size: 0.875rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        button:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .btn-primary {
            background: #3b82f6;
            color: white;
        }
        
        .btn-secondary {
            background: #64748b;
            color: white;
        }
        
        .btn-success {
            background: #059669;
            color: white;
        }
        
        .btn-warning {
            background: #d97706;
            color: white;
        }
        
        .btn-ghost {
            background: transparent;
            color: #64748b;
            border: 1px solid #e2e8f0;
        }
        
        .btn-icon {
            padding: 0.5rem;
            width: 36px;
            height: 36px;
            justify-content: center;
        }
        
        /* Form Elements */
        .form-row {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        
        .form-group {
            flex: 1;
        }
        
        label {
            display: block;
            font-size: 0.875rem;
            font-weight: 500;
            color: #475569;
            margin-bottom: 0.5rem;
        }
        
        input[type="number"] {
            width: 100%;
            padding: 0.5rem 0.75rem;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            font-size: 0.875rem;
            transition: border-color 0.2s;
        }
        
        input[type="number"]:focus {
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        
        /* Cards */
        .card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .card-title {
            font-size: 1rem;
            font-weight: 600;
            color: #1e293b;
        }
        
        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .stat-card {
            background: white;
            padding: 1.25rem;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .stat-label {
            font-size: 0.75rem;
            font-weight: 500;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }
        
        .stat-value {
            font-size: 1.75rem;
            font-weight: 700;
            color: #1e293b;
        }
        
        .stat-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 500;
            margin-top: 0.5rem;
        }
        
        .badge-success { background: #dcfce7; color: #166534; }
        .badge-warning { background: #fef3c7; color: #92400e; }
        .badge-info { background: #dbeafe; color: #1e40af; }
        
        /* Content Grid */
        .content-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.5rem;
        }
        
        /* Lists */
        .item-list {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .list-item {
            padding: 0.75rem;
            border-bottom: 1px solid #f1f5f9;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background 0.2s;
        }
        
        .list-item:hover {
            background: #f8fafc;
        }
        
        .list-item:last-child {
            border-bottom: none;
        }
        
        .item-name {
            font-weight: 500;
            color: #1e293b;
        }
        
        .item-detail {
            font-size: 0.875rem;
            color: #64748b;
        }
        
        .status-badge {
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        
        .status-traveling { background: #dbeafe; color: #1e40af; }
        .
        .status-boarding { background: #fef3c7; color: #92400e; }
        .status-at_station { background: #f1f5f9; color: #475569; }
        .status-arrived { background: #dcfce7; color: #166534; }
        
        /* Route List */
        .route-item {
            display: flex;
            justify-content: space-between;
            padding: 0.75rem;
            border-bottom: 1px solid #f1f5f9;
        }
        
        .route-item:last-child {
            border-bottom: none;
        }
        
        .route-name {
            font-weight: 500;
            color: #1e293b;
        }
        
        .route-price {
            font-weight: 600;
            color: #3b82f6;
        }
        
        /* Toggle Button */
        .toggle-sidebar {
            position: fixed;
            left: 280px;
            top: 100px;
            background: white;
            border: 1px solid #e2e8f0;
            border-left: none;
            border-radius: 0 6px 6px 0;
            padding: 0.5rem 0.25rem;
            cursor: pointer;
            transition: left 0.3s;
            z-index: 100;
        }
        
        .toggle-sidebar.sidebar-hidden {
            left: 0;
        }
        
        /* Responsive */
        @media (max-width: 1024px) {
            .content-grid {
                grid-template-columns: 1fr;
            }
        }
        
        @media (max-width: 768px) {
            .sidebar {
                position: fixed;
                left: 0;
                top: 88px;
                height: calc(100vh - 88px);
                z-index: 50;
                box-shadow: 2px 0 8px rgba(0,0,0,0.1);
            }
            
            .toolbar {
                flex-direction: column;
                gap: 1rem;
            }
            
            .toolbar-left, .toolbar-right {
                width: 100%;
                justify-content: space-between;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Highway Bus Depot</h1>
        <p>Multi-Agent Based Real-time Monitoring System</p>
    </div>

    <div class="toggle-sidebar" id="toggleBtn" onclick="toggleSidebar()">
        <span id="toggleIcon">◀</span>
    </div>

    <div class="container">
        <div class="sidebar" id="sidebar">
            <div class="sidebar-section">
                <h3>Simulation Setup</h3>
                <div class="form-group">
                    <label for="num_passengers">Passengers</label>
                    <input type="number" id="num_passengers" value="10" min="1" max="200">
                </div>
                <div class="form-group">
                    <label for="num_buses">Buses</label>
                    <input type="number" id="num_buses" value="4" min="1" max="20">
                </div>
                <button class="btn-primary" style="width: 100%; margin-top: 1rem;" onclick="createSimulation()">
                    Initialize System
                </button>
            </div>

            <div class="sidebar-section">
                <h3>Available Routes</h3>
                <div class="route-item">
                    <span class="route-name">Kottawa</span>
                    <span class="route-price">LKR 150</span>
                </div>
                <div class="route-item">
                    <span class="route-name">Maharagama</span>
                    <span class="route-price">LKR 200</span>
                </div>
                <div class="route-item">
                    <span class="route-name">Kaduwela</span>
                    <span class="route-price">LKR 150</span>
                </div>
                <div class="route-item">
                    <span class="route-name">Mathugama</span>
                    <span class="route-price">LKR 400</span>
                </div>
                <div class="route-item">
                    <span class="route-name">Moratuwa</span>
                    <span class="route-price">LKR 320</span>
                </div>
                <div class="route-item">
                    <span class="route-name">Kandy</span>
                    <span class="route-price">LKR 640</span>
                </div>
                <div class="route-item">
                    <span class="route-name">Galle</span>
                    <span class="route-price">LKR 890</span>
                </div>
                <div class="route-item">
                    <span class="route-name">Matara</span>
                    <span class="route-price">LKR 1080</span>
                </div>
            </div>
        </div>

        <div class="main-content">
            <div class="toolbar">
                <div class="toolbar-left">
                    <button class="btn-success" onclick="startSimulation()">
                        ▶ Auto Run
                    </button>
                    <button class="btn-warning" onclick="stepSimulation()">
                        → Step
                    </button>
                    <button class="btn-secondary" onclick="stopSimulation()">
                        ⏸ Stop
                    </button>
                    <button class="btn-ghost" onclick="resetSimulation()">
                        ↻ Reset
                    </button>
                </div>
                <div class="toolbar-right">
                    <span style="font-size: 0.875rem; color: #64748b;">
                        Step: <strong id="current-step">0</strong>
                    </span>
                    <span class="stat-badge badge-info" id="sim-status">Stopped</span>
                </div>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Tickets Sold</div>
                    <div class="stat-value" id="tickets-sold">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Revenue</div>
                    <div class="stat-value" id="revenue">LKR 0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Queue Length</div>
                    <div class="stat-value" id="queue-length">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Active Buses</div>
                    <div class="stat-value" id="active-buses">0</div>
                </div>
            </div>

            <div class="content-grid">
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Bus Fleet</h2>
                    </div>
                    <div class="item-list" id="buses-list">
                        <div style="text-align: center; padding: 2rem; color: #94a3b8;">
                            No buses initialized
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Passengers</h2>
                    </div>
                    <div class="item-list" id="passengers-list">
                        <div style="text-align: center; padding: 2rem; color: #94a3b8;">
                            No passengers
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let updateInterval;
        let sidebarVisible = true;

        function toggleSidebar() {
            sidebarVisible = !sidebarVisible;
            const sidebar = document.getElementById('sidebar');
            const toggleBtn = document.getElementById('toggleBtn');
            const toggleIcon = document.getElementById('toggleIcon');
            
            if (sidebarVisible) {
                sidebar.classList.remove('hidden');
                toggleBtn.classList.remove('sidebar-hidden');
                toggleIcon.textContent = '◀';
            } else {
                sidebar.classList.add('hidden');
                toggleBtn.classList.add('sidebar-hidden');
                toggleIcon.textContent = '▶';
            }
        }

        function createSimulation() {
            const numPassengers = document.getElementById('num_passengers').value;
            const numBuses = document.getElementById('num_buses').value;
            
            fetch('/create', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    num_passengers: parseInt(numPassengers),
                    num_buses: parseInt(numBuses)
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                updateDashboard();
            });
        }

        function startSimulation() {
            fetch('/start', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    console.log(data.message);
                    if (!updateInterval) {
                        updateInterval = setInterval(updateDashboard, 1000);
                    }
                });
        }

        function stepSimulation() {
            fetch('/step', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    console.log(data.message);
                    updateDashboard();
                });
        }

        function stopSimulation() {
            fetch('/stop', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    console.log(data.message);
                    if (updateInterval) {
                        clearInterval(updateInterval);
                        updateInterval = null;
                    }
                });
        }

        function resetSimulation() {
            fetch('/reset', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    console.log(data.message);
                    if (updateInterval) {
                        clearInterval(updateInterval);
                        updateInterval = null;
                    }
                    updateDashboard();
                });
        }

        function updateDashboard() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    // Update stats
                    document.getElementById('tickets-sold').textContent = data.tickets_sold;
                    document.getElementById('revenue').textContent = 'LKR ' + data.revenue.toLocaleString();
                    document.getElementById('queue-length').textContent = data.queue_length;
                    document.getElementById('current-step').textContent = data.current_step;
                    document.getElementById('active-buses').textContent = data.buses.filter(b => b.state !== 'at_station').length;
                    
                    const statusBadge = document.getElementById('sim-status');
                    if (data.running) {
                        statusBadge.textContent = 'Running';
                        statusBadge.className = 'stat-badge badge-success';
                    } else {
                        statusBadge.textContent = 'Stopped';
                        statusBadge.className = 'stat-badge badge-info';
                    }

                    // Update buses
                    const busesList = document.getElementById('buses-list');
                    if (data.buses.length === 0) {
                        busesList.innerHTML = '<div style="text-align: center; padding: 2rem; color: #94a3b8;">No buses initialized</div>';
                    } else {
                        busesList.innerHTML = data.buses.map(bus => `
                            <div class="list-item">
                                <div>
                                    <div class="item-name">${bus.id}</div>
                                    <div class="item-detail">${bus.route} • ${bus.passengers}/${bus.capacity} passengers</div>
                                </div>
                                <span class="status-badge status-${bus.state.replace(' ', '_')}">${bus.state}</span>
                            </div>
                        `).join('');
                    }

                    // Update passengers
                    const passengersList = document.getElementById('passengers-list');
                    if (data.passengers.length === 0) {
                        passengersList.innerHTML = '<div style="text-align: center; padding: 2rem; color: #94a3b8;">No passengers</div>';
                    } else {
                        const displayPassengers = data.passengers.slice(0, 20);
                        passengersList.innerHTML = displayPassengers.map(p => `
                            <div class="list-item">
                                <div>
                                    <div class="item-name">${p.id}</div>
                                    <div class="item-detail">${p.destination}</div>
                                </div>
                                <span class="status-badge status-${p.state.replace(' ', '_')}">${p.state}</span>
                            </div>
                        `).join('');
                        
                        if (data.passengers.length > 20) {
                            passengersList.innerHTML += `<div style="text-align: center; padding: 1rem; color: #64748b; font-size: 0.875rem;">+ ${data.passengers.length - 20} more</div>`;
                        }
                    }
                });
        }

        // Initial load
        updateDashboard();
    </script>
</body>
</html>
"""

def run_simulation():
    """Run simulation in background thread"""
    global simulation_running, model
    while simulation_running:
        if model:
            model.step()
        time.sleep(1)  # 1 step per second

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/create', methods=['POST'])
def create():
    global model, simulation_running
    simulation_running = False
    time.sleep(0.5)
    
    data = request.get_json()
    num_passengers = data.get('num_passengers', 10)
    num_buses = data.get('num_buses', 4)
    
    model = BusStationModel(num_passengers=num_passengers, num_buses=num_buses)
    return jsonify({'message': f'Simulation created with {num_passengers} passengers and {num_buses} buses'})

@app.route('/start', methods=['POST'])
def start():
    global simulation_running, simulation_thread, model
    
    if not model:
        model = BusStationModel(num_passengers=10, num_buses=4)
    
    if not simulation_running:
        simulation_running = True
        simulation_thread = threading.Thread(target=run_simulation, daemon=True)
        simulation_thread.start()
        return jsonify({'message': 'Simulation started (auto-running)'})
    return jsonify({'message': 'Simulation already running'})

@app.route('/step', methods=['POST'])
def step():
    global model
    if not model:
        model = BusStationModel(num_passengers=10, num_buses=4)
    
    model.step()
    return jsonify({'message': 'Stepped once'})

@app.route('/stop', methods=['POST'])
def stop():
    global simulation_running
    simulation_running = False
    return jsonify({'message': 'Simulation stopped'})

@app.route('/reset', methods=['POST'])
def reset():
    global model, simulation_running
    simulation_running = False
    time.sleep(0.5)
    model = BusStationModel(num_passengers=10, num_buses=4)
    return jsonify({'message': 'Simulation reset'})

@app.route('/status')
def status():
    global simulation_running
    if not model:
        return jsonify({
            'tickets_sold': 0,
            'revenue': 0,
            'queue_length': 0,
            'current_step': 0,
            'running': False,
            'buses': [],
            'passengers': []
        })
    
    return jsonify({
        'tickets_sold': model.station.tickets_sold,
        'revenue': model.station.revenue,
        'queue_length': len(model.station.ticket_queue),
        'current_step': model.schedule.steps,
        'running': simulation_running,
        'buses': [{
            'id': bus.unique_id,
            'route': bus.route,
            'state': bus.state,
            'passengers': len(bus.passengers),
            'capacity': bus.capacity
        } for bus in model.buses],
        'passengers': [{
            'id': p.unique_id,
            'destination': p.destination,
            'state': p.state
        } for p in model.passengers]
    })

if __name__ == '__main__':
    print("Starting Kadawatha Highway Bus Depot Dashboard...")
    print("Visit: http://localhost:5000")
    app.run(debug=True, use_reloader=False)