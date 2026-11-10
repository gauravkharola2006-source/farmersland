#!/usr/bin/env python3
"""
HTTP Server to bridge web UI with C backend
Run this server to enable the web UI to interact with the smart farming system
"""

import json
import subprocess
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import tempfile

# Configuration
C_BINARY = './smart_farming_system.exe' if sys.platform == 'win32' else './smart_farming_system'
PORT = int(os.environ.get('FARM_PORT', '8000'))
STATE_FILE = os.environ.get('FARM_STATE_FILE', 'ui_state.txt')

class Field:
    """Simple Field class to match C structure"""
    def __init__(self, field_id, moisture, crop):
        self.fieldID = field_id
        self.moisture = moisture
        self.crop = crop
    
    def to_dict(self):
        return {
            'id': self.fieldID,
            'moisture': self.moisture,
            'crop': self.crop,
            'dryness': 100 - self.moisture
        }

class FarmingAPIHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.fields = {}  # field_id -> Field
        self.queue = []  # Simple queue
        self.heap = []  # Priority heap (dryness-based)
        self.load_state()
        super().__init__(*args, **kwargs)
    
    def load_state(self):
        """Load fields from state file"""
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 3:
                            field_id = int(parts[0])
                            moisture = int(parts[1])
                            crop = ' '.join(parts[2:])
                            self.fields[field_id] = Field(field_id, moisture, crop)
            except Exception as e:
                print(f"Warning: Could not load state: {e}")
    
    def save_state(self):
        """Save fields to state file"""
        try:
            with open(STATE_FILE, 'w') as f:
                for field in sorted(self.fields.values(), key=lambda x: x.fieldID):
                    f.write(f"{field.fieldID} {field.moisture} {field.crop}\n")
        except Exception as e:
            print(f"Warning: Could not save state: {e}")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/api/list_fields':
            self.handle_list_fields()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body.decode('utf-8')) if body else {}
        except:
            data = {}
        
        path = urlparse(self.path).path
        
        if path == '/api/add_field':
            self.handle_add_field(data)
        elif path == '/api/remove_field':
            self.handle_remove_field(data)
        elif path == '/api/list_fields':
            self.handle_list_fields()
        elif path == '/api/enqueue':
            self.handle_enqueue(data)
        elif path == '/api/dequeue':
            self.handle_dequeue()
        elif path == '/api/build_heap':
            self.handle_build_heap()
        elif path == '/api/extract_max':
            self.handle_extract_max()
        elif path == '/api/schedule':
            self.handle_schedule(data)
        elif path == '/api/predict_yield':
            self.handle_predict_yield(data)
        elif path == '/api/plan_irrigation':
            self.handle_plan_irrigation(data)
        elif path == '/api/pipeline_bfs':
            self.handle_pipeline_bfs(data)
        elif path == '/api/save_fields':
            self.handle_save_fields(data)
        elif path == '/api/load_fields':
            self.handle_load_fields(data)
        else:
            self.send_error(404, "Not Found")
    
    def send_json_response(self, data, status=200):
        """Send JSON response with CORS headers"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def handle_add_field(self, data):
        """Add or update a field"""
        try:
            field_id = data.get('id')
            moisture = data.get('moisture')
            crop = data.get('crop')
            
            if field_id is None or moisture is None or not crop:
                self.send_json_response({'error': 'Missing required fields'}, 400)
                return
            
            if not (0 <= moisture <= 100):
                self.send_json_response({'error': 'Moisture must be between 0 and 100'}, 400)
                return
            
            self.fields[field_id] = Field(field_id, moisture, crop)
            self.save_state()
            self.send_json_response({'success': True, 'message': f'Field {field_id} added/updated'})
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def handle_remove_field(self, data):
        """Remove a field"""
        try:
            field_id = data.get('id')
            if field_id is None:
                self.send_json_response({'error': 'Missing field ID'}, 400)
                return
            
            if field_id in self.fields:
                del self.fields[field_id]
                self.save_state()
                self.send_json_response({'success': True, 'message': f'Field {field_id} removed'})
            else:
                self.send_json_response({'success': True, 'message': f'Field {field_id} not found'})
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def handle_list_fields(self):
        """List all fields"""
        try:
            fields_list = [field.to_dict() for field in sorted(self.fields.values(), key=lambda x: x.fieldID)]
            self.send_json_response({'fields': fields_list, 'count': len(fields_list)})
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def handle_enqueue(self, data):
        """Enqueue a field for irrigation"""
        try:
            field_id = data.get('id')
            if field_id is None:
                self.send_json_response({'error': 'Missing field ID'}, 400)
                return
            
            if field_id not in self.fields:
                self.send_json_response({'error': 'Field not found'}, 400)
                return
            
            if len(self.queue) >= 256:  # QUEUE_CAPACITY
                self.send_json_response({'error': 'Queue is full'}, 400)
                return
            
            self.queue.append(field_id)
            self.send_json_response({'success': True, 'message': f'Field {field_id} enqueued'})
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def handle_dequeue(self):
        """Dequeue next field from irrigation queue"""
        try:
            if not self.queue:
                self.send_json_response({'message': 'Queue is empty'})
                return
            
            field_id = self.queue.pop(0)
            self.send_json_response({'fieldId': field_id, 'success': True})
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def handle_build_heap(self):
        """Build priority heap from fields"""
        try:
            if not self.fields:
                self.send_json_response({'error': 'No fields available'}, 400)
                return
            
            self.heap.clear()   # change the shared list in place (do not rebind it)
            for field in self.fields.values():
                self.heap.append({
                    'id': field.fieldID,
                    'dryness': 100 - field.moisture,
                    'crop': field.crop
                })
            
            # Sort by dryness (max heap - highest dryness first)
            self.heap.sort(key=lambda x: x['dryness'], reverse=True)
            self.send_json_response({'success': True, 'message': f'Heap built with {len(self.heap)} fields'})
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def handle_extract_max(self):
        """Extract highest priority field from heap"""
        try:
            if not self.heap:
                self.send_json_response({'message': 'Heap is empty. Build heap first.'})
                return
            
            field = self.heap.pop(0)  # Already sorted, so first is max
            self.send_json_response({'field': field, 'success': True})
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def handle_schedule(self, data):
        """Heap -> queue scheduling (same rule as C++ menu option 13).
        Rebuilds the heap from the CURRENT fields, then moves the driest `count`
        fields into the irrigation queue, driest first."""
        try:
            try:
                count = int(data.get('count'))
            except (ValueError, TypeError):
                self.send_json_response({'error': 'count must be a number'}, 400)
                return
            if not (1 <= count <= 256):   # 256 = QUEUE_CAPACITY
                self.send_json_response({'error': 'count must be between 1 and 256'}, 400)
                return
            if not self.fields:
                self.send_json_response({'error': 'No fields available'}, 400)
                return

            # fresh heap from current data (dryness may have changed)
            self.heap.clear()
            for field in sorted(self.fields.values(), key=lambda x: x.fieldID):
                self.heap.append({'id': field.fieldID, 'dryness': 100 - field.moisture, 'crop': field.crop})
            self.heap.sort(key=lambda x: x['dryness'], reverse=True)

            scheduled = []
            while self.heap and len(scheduled) < count:
                if len(self.queue) >= 256:   # queue full
                    break
                item = self.heap.pop(0)
                self.queue.append(item['id'])
                scheduled.append({'id': item['id'], 'dryness': item['dryness'], 'crop': item['crop']})

            if not scheduled:
                self.send_json_response({'error': 'Queue is full'}, 400)
                return
            self.send_json_response({
                'success': True,
                'moved': len(scheduled),
                'scheduled': scheduled,
                'queueLength': len(self.queue),
                'message': f'{len(scheduled)} field(s) moved from heap to irrigation queue (driest first)'
            })
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)

    def handle_predict_yield(self, data):
        """Predict yield for a field using moisture-based formula"""
        try:
            field_id = data.get('id')
            if field_id is None:
                self.send_json_response({'error': 'Missing field ID'}, 400)
                return
            
            # Convert to int if it's a string
            try:
                field_id = int(field_id)
            except (ValueError, TypeError):
                self.send_json_response({'error': 'Invalid field ID - must be a number'}, 400)
                return
            
            if field_id not in self.fields:
                self.send_json_response({'error': 'Field not found'}, 400)
                return
            
            field = self.fields[field_id]
            
            # Use the same formula as prediction.c
            # score = 1.0 - ((m - 50.0) * (m - 50.0)) / (50.0 * 50.0)
            m = float(field.moisture)
            score = 1.0 - ((m - 50.0) * (m - 50.0)) / (50.0 * 50.0)
            if score < 0:
                score = 0.0
            
            yield_val = score   # same 0-1 relative scale as the C++ program (menu option 8)
            
            self.send_json_response({'yield': round(yield_val, 2), 'success': True})
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def handle_plan_irrigation(self, data):
        """Plan multi-day irrigation using C binary"""
        try:
            days = data.get('days')
            per_day = data.get('perDay')
            
            if days is None or per_day is None:
                self.send_json_response({'error': 'Missing days or perDay'}, 400)
                return

            try:
                days = int(days)
                per_day = int(per_day)
            except (ValueError, TypeError):
                self.send_json_response({'error': 'Days and perDay must be numbers'}, 400)
                return
            if not (1 <= days <= 365) or not (1 <= per_day <= 1000):
                self.send_json_response({'error': 'Days must be 1-365 and perDay must be 1-1000'}, 400)
                return
            
            if not self.fields:
                self.send_json_response({'error': 'No fields available'}, 400)
                return
            
            # Save current state to temp file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp:
                for field in sorted(self.fields.values(), key=lambda x: x.fieldID):
                    tmp.write(f"{field.fieldID} {field.moisture} {field.crop}\n")
                tmp_filename = tmp.name
            
            try:
                # Use C binary for planning
                process = subprocess.Popen(
                    [C_BINARY],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=os.path.dirname(os.path.abspath(__file__))
                )
                
                inputs = f"11\n{tmp_filename}\n9\n{days}\n{per_day}\n0\n"
                stdout, stderr = process.communicate(input=inputs, timeout=10)
                
                schedule = []
                if 'Planned for' in stdout:
                    for line in stdout.split('\n'):
                        if 'Day' in line and ':' in line:
                            parts = line.split(':')
                            if len(parts) > 1:
                                field_ids = [int(x.strip()) for x in parts[1].strip().split() if x.strip().isdigit()]
                                schedule.append(field_ids)
                
                if schedule:
                    self.send_json_response({'schedule': schedule, 'success': True})
                else:
                    # Fallback: simple greedy scheduling
                    fields_by_dryness = sorted(
                        [f for f in self.fields.values()],
                        key=lambda x: 100 - x.moisture,
                        reverse=True
                    )
                    schedule = []
                    prev = set()
                    for day in range(days):
                        day_fields = []
                        for f in fields_by_dryness:
                            if len(day_fields) >= per_day:
                                break
                            if f.fieldID in prev:
                                continue
                            day_fields.append(f.fieldID)
                        schedule.append(day_fields)
                        prev = set(day_fields)
                    self.send_json_response({'schedule': schedule, 'success': True})
            finally:
                try:
                    os.unlink(tmp_filename)
                except:
                    pass
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def handle_pipeline_bfs(self, data):
        """Find shortest path in pipeline network using BFS algorithm"""
        try:
            filename = data.get('file')
            source = data.get('source')
            target = data.get('target')
            
            if not filename or source is None or target is None:
                self.send_json_response({'error': 'Missing required fields'}, 400)
                return
            
            # Convert to int
            try:
                source = int(source)
                target = int(target)
            except (ValueError, TypeError):
                self.send_json_response({'error': 'Source and target must be numbers'}, 400)
                return
            
            if not os.path.exists(filename):
                self.send_json_response({'error': f'File {filename} not found'}, 400)
                return
            
            # Load graph from file
            edges = []
            max_node = -1
            try:
                with open(filename, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            u, v = int(parts[0]), int(parts[1])
                            edges.append((u, v))
                            max_node = max(max_node, u, v)
            except Exception as e:
                self.send_json_response({'error': f'Error reading file: {str(e)}'}, 400)
                return
            
            if max_node < 0:
                self.send_json_response({'error': 'No edges found in file'}, 400)
                return
            
            if source < 0 or source > max_node or target < 0 or target > max_node:
                self.send_json_response({'error': f'Source or target out of range (0-{max_node})'}, 400)
                return
            
            # Build adjacency list
            from collections import defaultdict, deque
            graph = defaultdict(list)
            for u, v in edges:
                graph[u].append(v)
                graph[v].append(u)  # Undirected graph
            
            # BFS to find shortest path
            queue = deque([(source, 0)])
            visited = {source}
            
            while queue:
                node, dist = queue.popleft()
                if node == target:
                    self.send_json_response({'distance': dist, 'success': True})
                    return
                
                for neighbor in graph[node]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, dist + 1))
            
            # No path found
            self.send_json_response({'distance': -1, 'message': 'No path found', 'success': True})
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def handle_save_fields(self, data):
        """Save fields to file"""
        try:
            filename = data.get('filename')
            if not filename:
                self.send_json_response({'error': 'Missing filename'}, 400)
                return
            
            self.save_state()
            # Copy state file to requested filename
            if os.path.exists(STATE_FILE):
                import shutil
                shutil.copy(STATE_FILE, filename)
                self.send_json_response({'success': True, 'message': f'Fields saved to {filename}'})
            else:
                # Save directly
                with open(filename, 'w') as f:
                    for field in sorted(self.fields.values(), key=lambda x: x.fieldID):
                        f.write(f"{field.fieldID} {field.moisture} {field.crop}\n")
                self.send_json_response({'success': True, 'message': f'Fields saved to {filename}'})
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def handle_load_fields(self, data):
        """Load fields from file"""
        try:
            filename = data.get('filename')
            if not filename:
                self.send_json_response({'error': 'Missing filename'}, 400)
                return
            
            if not os.path.exists(filename):
                self.send_json_response({'error': f'File {filename} not found'}, 400)
                return
            
            # Load fields (same rules as the C++ loader: skip malformed lines and moisture outside 0-100)
            loaded = {}
            with open(filename, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) < 3:
                        continue
                    try:
                        field_id = int(parts[0])
                        moisture = int(parts[1])
                    except ValueError:
                        continue
                    if field_id < 0 or not (0 <= moisture <= 100):
                        continue
                    loaded[field_id] = Field(field_id, moisture, ' '.join(parts[2:]))
            self.fields.clear()   # change the shared dict in place (do not rebind it)
            self.fields.update(loaded)
            self.heap.clear()     # old heap no longer matches the fields
            
            self.save_state()  # Update state file
            self.send_json_response({'success': True, 'message': f'Fields loaded from {filename}'})
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def log_message(self, format, *args):
        """Override to reduce log noise"""
        pass

# Global handler instance to maintain state
_handler_instance = None

def handler_factory():
    """Factory to create handler with shared state"""
    global _handler_instance
    if _handler_instance is None:
        class StatefulHandler(FarmingAPIHandler):
            def __init__(self, *args, **kwargs):
                # Use module-level state
                if not hasattr(handler_factory, 'fields'):
                    handler_factory.fields = {}
                    handler_factory.queue = []
                    handler_factory.heap = []
                    handler_factory.load_state()
                
                # Copy state to instance
                self.fields = handler_factory.fields
                self.queue = handler_factory.queue
                self.heap = handler_factory.heap
                BaseHTTPRequestHandler.__init__(self, *args, **kwargs)
        
        handler_factory.fields = {}
        handler_factory.queue = []
        handler_factory.heap = []
        
        # Load initial state
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 3:
                            field_id = int(parts[0])
                            moisture = int(parts[1])
                            crop = ' '.join(parts[2:])
                            handler_factory.fields[field_id] = Field(field_id, moisture, crop)
            except Exception as e:
                print(f"Warning: Could not load state: {e}")
        
        handler_factory.load_state = lambda: None  # Placeholder
        handler_factory.save_state = lambda: None  # Placeholder
        
        return StatefulHandler
    return FarmingAPIHandler

def main():
    """Start the HTTP server"""
    # Check if C binary exists
    if not os.path.exists(C_BINARY):
        print(f"Warning: C binary not found at {C_BINARY}")
        print("Some features (yield prediction, irrigation planning, BFS) may not work")
        print("Please compile the project first using: make")
    
    # Create handler class with shared state
    class SharedStateHandler(FarmingAPIHandler):
        _fields = {}
        _queue = []
        _heap = []
        
        def __init__(self, *args, **kwargs):
            # Use class-level shared state
            if not SharedStateHandler._fields:
                SharedStateHandler.load_shared_state()
            self.fields = SharedStateHandler._fields
            self.queue = SharedStateHandler._queue
            self.heap = SharedStateHandler._heap
            BaseHTTPRequestHandler.__init__(self, *args, **kwargs)
        
        def save_state(self):
            """Save to both instance and class state"""
            try:
                with open(STATE_FILE, 'w') as f:
                    for field in sorted(self.fields.values(), key=lambda x: x.fieldID):
                        f.write(f"{field.fieldID} {field.moisture} {field.crop}\n")
            except Exception as e:
                print(f"Warning: Could not save state: {e}")
        
        @staticmethod
        def load_shared_state():
            """Load shared state from file"""
            if os.path.exists(STATE_FILE):
                try:
                    with open(STATE_FILE, 'r') as f:
                        for line in f:
                            parts = line.strip().split()
                            if len(parts) >= 3:
                                field_id = int(parts[0])
                                moisture = int(parts[1])
                                crop = ' '.join(parts[2:])
                                SharedStateHandler._fields[field_id] = Field(field_id, moisture, crop)
                except Exception as e:
                    print(f"Warning: Could not load state: {e}")
    
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, SharedStateHandler)
    
    print(f"Smart Farming System API Server")
    print(f"Server running on http://localhost:{PORT}")
    print(f"Open ui/index.html in your browser")
    print(f"Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()

if __name__ == '__main__':
    main()

