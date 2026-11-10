const API_BASE = 'http://localhost:8000/api';

// Helper function to make API calls
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(`${API_BASE}/${endpoint}`, options);
        const result = await response.json();
        return result;
    } catch (error) {
        return { error: `Network error: ${error.message}` };
    }
}

// Field Management Functions
async function addField() {
    const id = document.getElementById('fieldId').value;
    const moisture = document.getElementById('moisture').value;
    const crop = document.getElementById('crop').value;
    
    if (!id || !moisture || !crop) {
        showMessage('fieldsList', 'Please fill in all fields', 'error');
        return;
    }
    
    showMessage('fieldsList', 'Adding field...', 'loading');
    const result = await apiCall('add_field', 'POST', { id: parseInt(id), moisture: parseInt(moisture), crop });
    
    if (result.error) {
        showMessage('fieldsList', `Error: ${result.error}`, 'error');
    } else {
        showMessage('fieldsList', `Field ${id} added/updated successfully!`, 'success');
        document.getElementById('fieldId').value = '';
        document.getElementById('moisture').value = '';
        document.getElementById('crop').value = '';
    }
}

async function removeField() {
    const id = document.getElementById('removeFieldId').value;
    
    if (!id) {
        showMessage('fieldsList', 'Please enter a field ID', 'error');
        return;
    }
    
    showMessage('fieldsList', 'Removing field...', 'loading');
    const result = await apiCall('remove_field', 'POST', { id: parseInt(id) });
    
    if (result.error) {
        showMessage('fieldsList', `Error: ${result.error}`, 'error');
    } else {
        showMessage('fieldsList', result.message || `Field ${id} removed (if it existed)`, 'success');
        document.getElementById('removeFieldId').value = '';
    }
}

// Sample fields shown the first time "List All Fields" is pressed (same data as fields_sample.txt).
// After that you can add, update or remove fields as usual.
const SAMPLE_FIELDS = [
    { id: 1, moisture: 30, crop: 'wheat' },
    { id: 2, moisture: 45, crop: 'maize' },
    { id: 3, moisture: 20, crop: 'rice' },
    { id: 4, moisture: 70, crop: 'soybean' },
    { id: 5, moisture: 25, crop: 'barley' }
];

async function addSampleFieldsOnce() {
    let alreadyDone = false;
    try { alreadyDone = localStorage.getItem('sampleFieldsAdded') === 'yes'; } catch (e) {}
    if (alreadyDone) return;

    const current = await apiCall('list_fields');
    if (current.error) return;
    const existingIds = new Set((current.fields || []).map(f => f.id));

    // Only add sample fields whose ID is not already used, so fields you typed are kept.
    for (const f of SAMPLE_FIELDS) {
        if (!existingIds.has(f.id)) {
            await apiCall('add_field', 'POST', f);
        }
    }
    try { localStorage.setItem('sampleFieldsAdded', 'yes'); } catch (e) {}
}

async function listFields() {
    showMessage('fieldsList', 'Loading fields...', 'loading');
    await addSampleFieldsOnce();
    const result = await apiCall('list_fields');
    
    if (result.error) {
        showMessage('fieldsList', `Error: ${result.error}`, 'error');
    } else {
        if (result.fields && result.fields.length > 0) {
            const fieldsText = result.fields.map(f => 
                `ID: ${f.id} | Moisture: ${f.moisture}% | Crop: ${f.crop} | Dryness: ${100 - f.moisture}%`
            ).join('\n');
            showMessage('fieldsList', `Total Fields: ${result.fields.length}\n\n${fieldsText}`, 'success');
        } else {
            showMessage('fieldsList', 'No fields found.', '');
        }
    }
}

// Irrigation Queue Functions
async function enqueueField() {
    const id = document.getElementById('queueFieldId').value;
    
    if (!id) {
        showMessage('queueStatus', 'Please enter a field ID', 'error');
        return;
    }
    
    showMessage('queueStatus', 'Enqueueing field...', 'loading');
    const result = await apiCall('enqueue', 'POST', { id: parseInt(id) });
    
    if (result.error) {
        showMessage('queueStatus', `Error: ${result.error}`, 'error');
    } else {
        showMessage('queueStatus', result.message || `Field ${id} enqueued successfully!`, 'success');
        document.getElementById('queueFieldId').value = '';
    }
}

async function dequeueField() {
    showMessage('queueStatus', 'Dequeueing...', 'loading');
    const result = await apiCall('dequeue', 'POST');
    
    if (result.error) {
        showMessage('queueStatus', `Error: ${result.error}`, 'error');
    } else {
        if (result.fieldId !== undefined) {
            showMessage('queueStatus', `Dequeued field ID: ${result.fieldId}`, 'success');
        } else {
            showMessage('queueStatus', result.message || 'Queue is empty', '');
        }
    }
}

// Heap -> Queue scheduling (console menu option 13)
async function scheduleFromHeap() {
    const count = document.getElementById('scheduleCount').value;
    if (!count) {
        showMessage('queueStatus', 'Please enter how many fields to schedule', 'error');
        return;
    }
    showMessage('queueStatus', 'Scheduling from heap...', 'loading');
    const result = await apiCall('schedule', 'POST', { count: parseInt(count) });
    if (result.error) {
        showMessage('queueStatus', `Error: ${result.error}`, 'error');
    } else {
        const lines = result.scheduled.map((f, i) => `${i + 1}. Field ${f.id} (dryness ${f.dryness}%, ${f.crop})`);
        showMessage('queueStatus', `${result.message}\n\n${lines.join('\n')}\n\nQueue length: ${result.queueLength}`, 'success');
    }
}

// Priority Heap Functions
async function buildHeap() {
    showMessage('heapStatus', 'Building heap from fields...', 'loading');
    const result = await apiCall('build_heap', 'POST');
    
    if (result.error) {
        showMessage('heapStatus', `Error: ${result.error}`, 'error');
    } else {
        showMessage('heapStatus', result.message || 'Heap built successfully!', 'success');
    }
}

async function extractMax() {
    showMessage('heapStatus', 'Extracting highest priority field...', 'loading');
    const result = await apiCall('extract_max', 'POST');
    
    if (result.error) {
        showMessage('heapStatus', `Error: ${result.error}`, 'error');
    } else {
        if (result.field) {
            const f = result.field;
            showMessage('heapStatus', 
                `Highest Priority Field:\nID: ${f.id}\nDryness: ${f.dryness}%\nCrop: ${f.crop}`, 
                'success'
            );
        } else {
            showMessage('heapStatus', result.message || 'Heap is empty', '');
        }
    }
}

// Yield Prediction Function
async function predictYield() {
    const id = document.getElementById('predictFieldId').value;
    
    if (!id) {
        showMessage('predictionResult', 'Please enter a field ID', 'error');
        return;
    }
    
    showMessage('predictionResult', 'Calculating prediction...', 'loading');
    const result = await apiCall('predict_yield', 'POST', { id: parseInt(id) });
    
    if (result.error) {
        showMessage('predictionResult', `Error: ${result.error}`, 'error');
    } else {
        if (result.yield !== undefined) {
            showMessage('predictionResult', 
                `Field ID: ${id}\nPredicted Yield (relative): ${result.yield.toFixed(2)}`, 
                'success'
            );
        } else {
            showMessage('predictionResult', result.message || 'Prediction failed', 'error');
        }
    }
}

// Irrigation Planning Function
async function planIrrigation() {
    const days = document.getElementById('planDays').value;
    const perDay = document.getElementById('planPerDay').value;
    
    if (!days || !perDay) {
        showMessage('planResult', 'Please enter both days and fields per day', 'error');
        return;
    }
    
    showMessage('planResult', 'Generating irrigation plan...', 'loading');
    const result = await apiCall('plan_irrigation', 'POST', { 
        days: parseInt(days), 
        perDay: parseInt(perDay) 
    });
    
    if (result.error) {
        showMessage('planResult', `Error: ${result.error}`, 'error');
    } else {
        if (result.schedule && result.schedule.length > 0) {
            let planText = `Irrigation Plan (${result.schedule.length} days):\n\n`;
            result.schedule.forEach((day, index) => {
                planText += `Day ${index + 1}: ${day.join(', ') || 'No fields'}\n`;
            });
            showMessage('planResult', planText, 'success');
        } else {
            showMessage('planResult', result.message || 'No plan generated', '');
        }
    }
}

// Pipeline Network Function
async function findShortestPath() {
    const file = document.getElementById('networkFile').value;
    const source = document.getElementById('sourceNode').value;
    const target = document.getElementById('targetNode').value;
    
    if (!file || source === '' || target === '') {
        showMessage('pathResult', 'Please fill in all fields', 'error');
        return;
    }
    
    showMessage('pathResult', 'Finding shortest path...', 'loading');
    const result = await apiCall('pipeline_bfs', 'POST', { 
        file, 
        source: parseInt(source), 
        target: parseInt(target) 
    });
    
    if (result.error) {
        showMessage('pathResult', `Error: ${result.error}`, 'error');
    } else {
        if (result.distance !== undefined && result.distance >= 0) {
            showMessage('pathResult', 
                `Shortest path from node ${source} to node ${target}: ${result.distance} edges`, 
                'success'
            );
        } else {
            showMessage('pathResult', result.message || 'No path found or error occurred', 'error');
        }
    }
}

// File Operations Functions
async function saveFields() {
    const filename = document.getElementById('saveFilename').value;
    
    if (!filename) {
        showMessage('fileStatus', 'Please enter a filename', 'error');
        return;
    }
    
    showMessage('fileStatus', 'Saving fields...', 'loading');
    const result = await apiCall('save_fields', 'POST', { filename });
    
    if (result.error) {
        showMessage('fileStatus', `Error: ${result.error}`, 'error');
    } else {
        showMessage('fileStatus', result.message || `Fields saved to ${filename}`, 'success');
        document.getElementById('saveFilename').value = '';
    }
}

async function loadFields() {
    const filename = document.getElementById('loadFilename').value;
    
    if (!filename) {
        showMessage('fileStatus', 'Please enter a filename', 'error');
        return;
    }
    
    showMessage('fileStatus', 'Loading fields...', 'loading');
    const result = await apiCall('load_fields', 'POST', { filename });
    
    if (result.error) {
        showMessage('fileStatus', `Error: ${result.error}`, 'error');
    } else {
        showMessage('fileStatus', result.message || `Fields loaded from ${filename}`, 'success');
        document.getElementById('loadFilename').value = '';
    }
}

// Helper function to display messages
function showMessage(elementId, message, type = '') {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.className = 'output-area';
    if (type) {
        element.classList.add(type);
    }
}

// Allow Enter key to submit forms
document.addEventListener('DOMContentLoaded', () => {
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const card = input.closest('.card');
                const button = card.querySelector('.btn-primary');
                if (button) {
                    button.click();
                }
            }
        });
    });
});






