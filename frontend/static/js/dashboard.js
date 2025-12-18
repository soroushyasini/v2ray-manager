const API_BASE = '/api';

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

// Fetch and display users
async function loadUsers() {
    try {
        const response = await fetch(`${API_BASE}/users`);
        const users = await response.json();
        
        const tbody = document.getElementById('users-tbody');
        
        if (users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4">No users found</td></tr>';
            return;
        }
        
        tbody.innerHTML = users.map(user => `
            <tr>
                <td>${user.name}</td>
                <td>${user.id}</td>
                <td>${user.alter_id}</td>
                <td>
                    <button class="action-btn qr-btn" onclick="showQRCode('${user.id}')">QR Code</button>
                    <button class="action-btn delete-btn" onclick="deleteUser('${user.id}')">Delete</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading users:', error);
        document.getElementById('users-tbody').innerHTML = '<tr><td colspan="4">Error loading users</td></tr>';
    }
}

// Add new user
document.getElementById('add-user-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('user-name').value;
    const alterId = parseInt(document.getElementById('alter-id').value);
    
    try {
        const response = await fetch(`${API_BASE}/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, alter_id: alterId }),
        });
        
        if (response.ok) {
            alert('User added successfully!');
            document.getElementById('add-user-form').reset();
            document.getElementById('alter-id').value = '64';
            loadUsers();
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (error) {
        console.error('Error adding user:', error);
        alert('Failed to add user');
    }
});

// Delete user
async function deleteUser(userId) {
    if (!confirm('Are you sure you want to delete this user?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/users/${userId}`, {
            method: 'DELETE',
        });
        
        if (response.ok) {
            alert('User deleted successfully!');
            loadUsers();
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (error) {
        console.error('Error deleting user:', error);
        alert('Failed to delete user');
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
