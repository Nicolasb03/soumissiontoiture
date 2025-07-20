from flask import Blueprint, jsonify, request
import requests
import os

google_api_bp = Blueprint('google_api', __name__)

# Récupération de la clé API depuis les variables d'environnement
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

@google_api_bp.route('/geocode', methods=['POST'])
def geocode_address():
    """
    Proxy pour l'API Google Geocoding
    """
    try:
        data = request.json
        address = data.get('address')
        
        if not address:
            return jsonify({'error': 'Adresse requise'}), 400
        
        if not GOOGLE_API_KEY:
            return jsonify({'error': 'Clé API Google non configurée'}), 500
        
        # Appel à l'API Google Geocoding
        geocoding_url = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {
            'address': address,
            'key': GOOGLE_API_KEY
        }
        
        response = requests.get(geocoding_url, params=params)
        
        if response.status_code != 200:
            return jsonify({'error': 'Erreur lors de l\'appel à l\'API Google'}), 500
        
        geocoding_data = response.json()
        
        # Retourner les données de géocodage
        return jsonify(geocoding_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors du géocodage: {str(e)}'}), 500

@google_api_bp.route('/solar-analysis', methods=['POST'])
def solar_analysis():
    """
    Proxy pour l'API Google Solar
    """
    try:
        data = request.json
        lat = data.get('lat')
        lng = data.get('lng')
        
        if not lat or not lng:
            return jsonify({'error': 'Latitude et longitude requises'}), 400
        
        if not GOOGLE_API_KEY:
            return jsonify({'error': 'Clé API Google non configurée'}), 500
        
        # Appel à l'API Google Solar
        solar_url = 'https://solar.googleapis.com/v1/buildingInsights:findClosest'
        params = {
            'location.latitude': lat,
            'location.longitude': lng,
            'key': GOOGLE_API_KEY
        }
        
        response = requests.get(solar_url, params=params)
        
        if response.status_code != 200:
            return jsonify({'error': 'Erreur lors de l\'appel à l\'API Solar'}), 500
        
        solar_data = response.json()
        
        # Retourner les données Solar
        return jsonify(solar_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'analyse solaire: {str(e)}'}), 500
