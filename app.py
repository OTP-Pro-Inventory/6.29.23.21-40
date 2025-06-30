from flask import Flask, request, jsonify, session, redirect, url_for, render_template, flash
from flask_cors import CORS
from functools import wraps
import json
import os
import uuid
from datetime import datetime
import logging

# Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Configuration
app.secret_key = os.environ.get('SECRET_KEY') or 'dev-secret-key-here'
app.config['DATA_FOLDER'] = os.path.join(app.instance_path, 'data')
os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User authentication
USERS = {
    "sallen": "Bigmac100",
    "bgaines": "Cheese100"
}

# File paths
INVENTORY_FILE = os.path.join(app.config['DATA_FOLDER'], 'inventory.json')
REMOVALS_FILE = os.path.join(app.config['DATA_FOLDER'], 'removals.json')
ACTIVITY_FILE = os.path.join(app.config['DATA_FOLDER'], 'activity.json')

def initialize_data_files():
    """Create data files if they don't exist with initial data"""
    defaults = {
        INVENTORY_FILE: [
            {"id": str(uuid.uuid4()), "name": "iPhone 13", "quantity": 8, "category": "Phones", "threshold": 5},
            {"id": str(uuid.uuid4()), "name": "MacBook Pro", "quantity": 3, "category": "Laptops", "threshold": 5},
            {"id": str(uuid.uuid4()), "name": "iPad Air", "quantity": 12, "category": "Tablets", "threshold": 5}
        ],
        REMOVALS_FILE: [],
        ACTIVITY_FILE: []
    }
    
    for file_path, default_data in defaults.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump(default_data, f, indent=2)
            logger.info(f"Created initial data file: {file_path}")

initialize_data_files()

def read_json(file_path):
    """Read JSON data from file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error reading {file_path}: {str(e)}")
        return []

def write_json(file_path, data):
    """Write data to JSON file"""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error writing to {file_path}: {str(e)}")
        raise

def log_activity(action):
    """Record user activities with timestamp"""
    if 'username' not in session:
        return
        
    activity = {
        "user": session['username'],
        "action": action,
        "timestamp": datetime.now().isoformat()
    }
    activities = read_json(ACTIVITY_FILE)
    activities.append(activity)
    write_json(ACTIVITY_FILE, activities)
    logger.info(f"Logged activity: {action}")

# [Keep all your existing routes the same, they're correct]
# [Only add these new ones:]

@app.route('/api/inventory/update', methods=['PUT'])
@login_required
def update_inventory():
    try:
        inventory_data = request.get_json()
        write_json(INVENTORY_FILE, inventory_data)
        log_activity("Updated entire inventory")
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Inventory update error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/removals/update', methods=['PUT'])
@login_required
def update_removals():
    try:
        removals_data = request.get_json()
        write_json(REMOVALS_FILE, removals_data)
        log_activity("Updated removals list")
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Removals update error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)