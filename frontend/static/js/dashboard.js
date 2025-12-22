const API_BASE = '/api';

// Format bytes to human readable
function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i];
}

// Fetch and display system stats
async function updateSystemStats() {
    try {
        const response = await fetch(`${API_BASE}/stats/system`);
        const data = await response.json();
        
        document.getElementById('cpu-usage').textContent = `${data.cpu.percent.toFixed(1)}%`;
        document.getElementById('memory-usage').textContent = `${data.memory.percent.toFixed(1)}%`;
        document.getElementById('disk-usage').textContent = `${data.disk.percent.toFixed(1)}%`;
    } catch (error) {
        console.error('Error fetching system stats:', error);
    }
}

// Fetch and display users with traffic stats
async function loadUsers() {
    try {
        const response = await fetch(`${API_BASE}/users`);
        const users = await response.json();
        
        const tbody = document.getElementById('users-tbody');
        
        if (users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6">No users found</td></tr>';
            return;
        }
        
        tbody.innerHTML = users.map(user => {
            const trafficPercent = user.traffic_limit > 0 
                ? ((user.traffic_used / user.traffic_limit) * 100).toFixed(1)
                : 0;
            
            const trafficWarning = trafficPercent > 80 ? 'style="color: #dc3545; font-weight: bold;"' : '';
            
            return `
            <tr>
                <td>${user.name}</td>
                <td><code>${user.id}</code></td>
                <td>${formatBytes(user.uplink)}</td>
                <td>${formatBytes(user.downlink)}</td>
                <td ${trafficWarning}>${formatBytes(user.traffic_used)}</td>
                <td>
                    <button class="action-btn qr-btn" onclick="showQRCode('${user.id}')" title="Generate QR Code">📱 QR</button>
                    <button class="action-btn reset-btn" onclick="resetStats('${user.id}')" title="Reset Traffic Stats">🔄 Reset</button>
                    <button class="action-btn delete-btn" onclick="deleteUser('${user.id}')" title="Delete User">🗑️ Delete</button>
                </td>
            </tr>
        `}).join('');
    } catch (error) {
        console.error('Error loading users:', error);
        document.getElementById('users-tbody').innerHTML = '<tr><td colspan="6">Error loading users</td></tr>';
    }
}

// Add new user
document.getElementById('add-user-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('user-name').value;
    const alterId = parseInt(document.getElementById('alter-id').value);
    const trafficLimit = parseInt(document.getElementById('traffic-limit').value);
    
    try {
        const response = await fetch(`${API_BASE}/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                name, 
                alter_id: alterId,
                traffic_limit: trafficLimit 
            }),
        });
        
        if (response.ok) {
            alert('✅ User added successfully! (No service interruption)');
            document.getElementById('add-user-form').reset();
            document.getElementById('alter-id').value = '64';
            document.getElementById('traffic-limit').value = '0';
            loadUsers();
        } else {
            const error = await response.json();
            alert(`❌ Error: ${error.detail}`);
        }
    } catch (error) {
        console.error('Error adding user:', error);
        alert('❌ Failed to add user');
    }
});

// Delete user
async function deleteUser(userId) {
    if (!confirm('⚠️ Are you sure you want to delete this user? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/users/${userId}`, {
            method: 'DELETE',
        });
        
        if (response.ok) {
            alert('✅ User deleted successfully! (No service interruption)');
            loadUsers();
        } else {
            const error = await response.json();
            alert(`❌ Error: ${error.detail}`);
        }
    } catch (error) {
        console.error('Error deleting user:', error);
        alert('❌ Failed to delete user');
    }
}

// Reset traffic stats
async function resetStats(userId) {
    if (!confirm('Reset traffic statistics for this user?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/users/${userId}/reset-stats`, {
            method: 'POST',
        });
        
        if (response.ok) {
            alert('✅ Traffic stats reset successfully!');
            loadUsers();
        } else {
            const error = await response.json();
            alert(`❌ Error: ${error.detail}`);
        }
    } catch (error) {
        console.error('Error resetting stats:', error);
        alert('❌ Failed to reset stats');
    }
}

// Show QR code
async function showQRCode(userId) {
    try {
        const response = await fetch(`${API_BASE}/users/${userId}/qrcode`);
        const data = await response.json();
        
        const modal = document.getElementById('qr-modal');
        const qrImage = document.getElementById('qr-image');
        
        qrImage.src = `data:image/png;base64,${data.qrcode}`;
        modal.style.display = 'block';
    } catch (error) {
        console.error('Error generating QR code:', error);
        alert('Failed to generate QR code');
    }
}

// Close modal
document.querySelector('.close').addEventListener('click', () => {
    document.getElementById('qr-modal').style.display = 'none';
});

window.addEventListener('click', (event) => {
    const modal = document.getElementById('qr-modal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});

// Initialize
updateSystemStats();
loadUsers();

// Refresh stats every 5 seconds
setInterval(updateSystemStats, 5000);
setInterval(loadUsers, 5000);  // Also refresh user traffic stats
