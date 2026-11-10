"""End-to-end API test: starts server.py and exercises every endpoint the web UI uses.

Also checks that every endpoint called in ui/script.js exists in server.py.
Run:  make && python3 tests/test_api.py      (or: make test)
Note: this tests the API the browser talks to. It does not click through the page in a browser.
"""
import json, os, re, socket, subprocess, sys, tempfile, time, urllib.request, urllib.error

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(ROOT)
fails = []

def check(name, cond, extra=''):
    print(('  ok   - ' if cond else '  FAIL - ') + name + ('' if cond else ' ' + str(extra)))
    if not cond:
        fails.append(name)

def free_port():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]; s.close(); return p

# ---- 1. every endpoint used by the UI exists in the server -------------------------------
ui_calls = set(re.findall(r"apiCall\('([a-z_]+)'", open('ui/script.js').read()))
srv_routes = set(re.findall(r"'/api/([a-z_]+)'", open('server.py').read()))
check('UI endpoints (%d) all exist in server.py' % len(ui_calls), ui_calls <= srv_routes, ui_calls - srv_routes)

if not os.path.exists('smart_farming_system'):
    subprocess.check_call(['make'], stdout=subprocess.DEVNULL)

port = free_port()
tmp = tempfile.mkdtemp()
env = dict(os.environ, FARM_PORT=str(port), FARM_STATE_FILE=os.path.join(tmp, 'state.txt'))
proc = subprocess.Popen([sys.executable, 'server.py'], env=env, stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
base = 'http://127.0.0.1:%d/api/' % port

def post(ep, data=None):
    req = urllib.request.Request(base + ep, data=json.dumps(data or {}).encode(),
                                 headers={'Content-Type': 'application/json'})
    try:
        r = urllib.request.urlopen(req, timeout=20)
        return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b'{}')

try:
    for _ in range(50):
        try: socket.create_connection(('127.0.0.1', port), timeout=0.2).close(); break
        except OSError: time.sleep(0.1)

    print('API end-to-end test')
    # add / validation
    st, r = post('add_field', {'id': 1, 'moisture': 30, 'crop': 'sweet corn'}); check('add field 1 (crop with space)', st == 200 and r.get('success'))
    post('add_field', {'id': 2, 'moisture': 20, 'crop': 'rice'})
    post('add_field', {'id': 3, 'moisture': 60, 'crop': 'wheat'})
    st, r = post('add_field', {'id': 4, 'moisture': 150, 'crop': 'x'}); check('moisture 150 rejected', st == 400)
    st, r = post('add_field', {'id': 4, 'crop': 'x'}); check('missing moisture rejected', st == 400)

    # list
    st, r = post('list_fields'); check('list returns 3 fields sorted by ID', r.get('count') == 3 and [f['id'] for f in r['fields']] == [1, 2, 3], r)

    # queue
    st, r = post('enqueue', {'id': 2}); check('enqueue existing field', st == 200 and r.get('success'))
    st, r = post('enqueue', {'id': 99}); check('enqueue missing field rejected', st == 400)
    st, r = post('dequeue'); check('dequeue gives field 2', r.get('fieldId') == 2, r)
    st, r = post('dequeue'); check('dequeue on empty queue', 'empty' in r.get('message', '').lower(), r)

    # heap
    st, r = post('extract_max'); check('extract before build -> build-first message', 'build' in r.get('message', '').lower(), r)
    st, r = post('build_heap'); check('build heap', st == 200 and r.get('success'), r)
    st, r = post('extract_max'); check('driest field first (id 2, dryness 80)', r.get('field', {}).get('id') == 2 and r['field']['dryness'] == 80, r)

    # heap -> queue scheduling (menu option 13 equivalent)
    st, r = post('schedule', {'count': 2}); check('schedule 2 driest from heap', st == 200 and r.get('moved') == 2 and r['scheduled'][0]['id'] == 2, r)
    st, r = post('dequeue'); check('queue holds driest first after schedule', r.get('fieldId') == 2, r)
    st, r = post('dequeue'); check('second scheduled field comes out next', r.get('success'), r)
    st, r = post('schedule', {'count': 0}); check('schedule count 0 rejected', st == 400)
    st, r = post('schedule', {'count': 'abc'}); check('schedule non-numeric rejected', st == 400)
    while post('dequeue')[1].get('fieldId') is not None: pass   # leave the queue empty for later tests

    # prediction: same 0-1 scale as the C++ program (moisture 30 -> 0.84)
    st, r = post('predict_yield', {'id': 1}); check('predict yield field 1 = 0.84 (matches C++ formula)', abs(r.get('yield', -1) - 0.84) < 1e-9, r)
    st, r = post('predict_yield', {'id': 99}); check('predict missing field rejected', st == 400)

    # planning goes through the C++ program
    st, r = post('plan_irrigation', {'days': 3, 'perDay': 2})
    check('plan 3 days x 2 (via C++): [[2,1],[3],[2,1]]', r.get('schedule') == [[2, 1], [3], [2, 1]], r)
    st, r = post('plan_irrigation', {'days': 0, 'perDay': 2}); check('plan with 0 days rejected', st == 400)
    st, r = post('plan_irrigation', {'days': 'x', 'perDay': 2}); check('plan with non-numeric days rejected', st == 400)

    # BFS
    st, r = post('pipeline_bfs', {'file': 'pipeline_network.txt', 'source': 0, 'target': 4}); check('BFS 0->4 = 3', r.get('distance') == 3, r)
    st, r = post('pipeline_bfs', {'file': 'pipeline_network.txt', 'source': 0, 'target': 99}); check('BFS out-of-range node rejected', st == 400)
    st, r = post('pipeline_bfs', {'file': 'nope.txt', 'source': 0, 'target': 1}); check('BFS missing file rejected', st == 400)

    # save / load / remove
    out = os.path.join(tmp, 'saved.txt')
    st, r = post('save_fields', {'filename': out}); check('save fields', st == 200 and os.path.exists(out), r)
    st, r = post('remove_field', {'id': 1}); check('remove field 1', st == 200)
    st, r = post('list_fields'); check('2 fields after remove', r.get('count') == 2, r)
    st, r = post('load_fields', {'filename': out}); check('load fields back', st == 200, r)
    st, r = post('list_fields'); check('3 fields after load (crop with space kept)', r.get('count') == 3 and r['fields'][0]['crop'] == 'sweet corn', r)
    st, r = post('load_fields', {'filename': os.path.join(tmp, 'missing.txt')}); check('load missing file rejected', st == 400)
finally:
    proc.kill()

if fails:
    print('API test FAILED (%d)' % len(fails)); sys.exit(1)
print('API test passed')
