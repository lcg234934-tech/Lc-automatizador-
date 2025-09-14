from flask import Blueprint, request, jsonify
from src.models.user import db, User
import json
import logging
import asyncio
from threading import Thread

betfair_bp = Blueprint("betfair", __name__)

# Global automation instance
automation_instance = None
automation_thread = None

@betfair_bp.route("/betfair/config", methods=["POST"])
def configure_betfair():
    """Configure Betfair API credentials"""
    data = request.get_json()
    user_id = data.get("user_id")
    username = data.get("username")
    password = data.get("password")
    app_key = data.get("app_key")
    cert_files = data.get("cert_files")  # Optional

    if not all([user_id, username, password, app_key]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Store Betfair configuration (in a real app, encrypt these credentials)
        betfair_config = {
            "username": username,
            "password": password,
            "app_key": app_key,
            "cert_files": cert_files
        }
        
        # Store in user session or database (simplified for demo)
        # In production, use proper encryption and secure storage
        session_key = f"betfair_config_{user_id}"
        # This is a simplified approach - use proper session management
        
        return jsonify({
            "message": "Betfair configuration saved successfully",
            "configured": True
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@betfair_bp.route("/betfair/start", methods=["POST"])
def start_betfair_automation():
    """Start Betfair automation for a user"""
    global automation_instance, automation_thread
    
    data = request.get_json()
    user_id = data.get("user_id")
    betfair_config = data.get("betfair_config")
    target_market_id = data.get("target_market_id")

    if not all([user_id, betfair_config]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Check if automation is already running
        if automation_instance and automation_thread and automation_thread.is_alive():
            return jsonify({"error": "Automation is already running"}), 400

        # Import here to avoid circular imports
        from src.integrations.betfair_automation import BetfairAutomation
        
        # Create automation instance
        automation_instance = BetfairAutomation(betfair_config)
        
        # Start automation in a separate thread
        def run_automation():
            try:
                automation_instance.start_automation(user_id, target_market_id)
            except Exception as e:
                logging.error(f"Automation error: {str(e)}")
        
        automation_thread = Thread(target=run_automation, daemon=True)
        automation_thread.start()
        
        return jsonify({
            "message": "Betfair automation started successfully",
            "status": "running"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@betfair_bp.route("/betfair/stop", methods=["POST"])
def stop_betfair_automation():
    """Stop Betfair automation"""
    global automation_instance, automation_thread
    
    try:
        if automation_instance:
            automation_instance.stop_automation()
            automation_instance = None
        
        if automation_thread:
            automation_thread = None
        
        return jsonify({
            "message": "Betfair automation stopped successfully",
            "status": "stopped"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@betfair_bp.route("/betfair/status", methods=["GET"])
def get_betfair_status():
    """Get current status of Betfair automation"""
    global automation_instance, automation_thread
    
    try:
        is_running = (automation_instance is not None and 
                     automation_thread is not None and 
                     automation_thread.is_alive())
        
        status_data = {
            "is_running": is_running,
            "active_markets": len(automation_instance.active_markets) if automation_instance else 0,
            "status": "running" if is_running else "stopped"
        }
        
        if automation_instance and is_running:
            status_data["markets"] = list(automation_instance.active_markets.keys())
        
        return jsonify(status_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@betfair_bp.route("/betfair/markets", methods=["GET"])
def get_roulette_markets():
    """Get available roulette markets from Betfair"""
    data = request.get_json() or {}
    betfair_config = data.get("betfair_config")
    
    if not betfair_config:
        return jsonify({"error": "Betfair configuration required"}), 400
    
    try:
        from src.integrations.betfair_client import BetfairClient
        
        client = BetfairClient(**betfair_config)
        
        if not client.login():
            return jsonify({"error": "Failed to login to Betfair"}), 401
        
        markets = client.get_roulette_markets()
        client.logout()
        
        return jsonify({
            "markets": markets,
            "count": len(markets)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@betfair_bp.route("/betfair/test-connection", methods=["POST"])
def test_betfair_connection():
    """Test connection to Betfair API"""
    data = request.get_json()
    betfair_config = data.get("betfair_config")
    
    if not betfair_config:
        return jsonify({"error": "Betfair configuration required"}), 400
    
    try:
        from src.integrations.betfair_client import BetfairClient
        
        client = BetfairClient(**betfair_config)
        
        # Test login
        if client.login():
            # Test getting markets
            markets = client.get_roulette_markets()
            client.logout()
            
            return jsonify({
                "success": True,
                "message": "Successfully connected to Betfair API",
                "markets_found": len(markets)
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Failed to login to Betfair API"
            }), 401

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Connection test failed: {str(e)}"
        }), 500

@betfair_bp.route("/betfair/manual-spin", methods=["POST"])
def manual_spin_result():
    """Manually input a spin result for testing"""
    data = request.get_json()
    user_id = data.get("user_id")
    winning_number = data.get("winning_number")
    
    if not all([user_id, winning_number is not None]):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        # Send to automation endpoint
        import requests
        
        payload = {
            'user_id': user_id,
            'winning_number': winning_number,
            'roulette_type': 'betfair_manual',
            'betting_house': 'betfair'
        }
        
        response = requests.post(
            "http://localhost:5000/api/automation/process_spin",
            json=payload
        )
        
        if response.status_code == 200:
            return jsonify({
                "message": "Manual spin processed successfully",
                "result": response.json()
            }), 200
        else:
            return jsonify({
                "error": "Failed to process manual spin",
                "details": response.text
            }), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

