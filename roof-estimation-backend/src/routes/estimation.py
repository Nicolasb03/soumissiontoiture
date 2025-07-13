from flask import Blueprint, jsonify, request
from src.models.lead import Lead
from src.models.user import db
import random
import math

estimation_bp = Blueprint('estimation', __name__)

# Données de coûts basées sur la recherche
MATERIAL_COSTS = {
    'tuiles_terre_cuite': {'min': 25, 'max': 90},  # €/m²
    'tuiles_beton': {'min': 35, 'max': 45},
    'bac_acier': {'min': 15, 'max': 35},
    'zinc': {'min': 40, 'max': 90},
    'ardoise': {'min': 60, 'max': 100}
}

LABOR_COST_PER_HOUR = 50  # €/heure
LABOR_HOURS_PER_SQM = 0.5  # heures par m²

COMPLEXITY_FACTORS = {
    'simple': 1.0,
    'moyenne': 1.2,
    'complexe': 1.5
}

def calculate_roof_estimation(address, roof_area=None):
    """
    Calcule une estimation de coût de rénovation de toiture
    """
    # Si pas de surface fournie, on estime entre 80 et 180 m²
    if roof_area is None:
        roof_area = random.randint(80, 180)
    
    # Sélection aléatoire du type de matériau (pour la démo)
    material_type = random.choice(list(MATERIAL_COSTS.keys()))
    material_costs = MATERIAL_COSTS[material_type]
    
    # Facteur de complexité aléatoire
    complexity = random.choice(list(COMPLEXITY_FACTORS.keys()))
    complexity_factor = COMPLEXITY_FACTORS[complexity]
    
    # Calcul des coûts
    material_cost_min = roof_area * material_costs['min']
    material_cost_max = roof_area * material_costs['max']
    
    labor_cost = roof_area * LABOR_HOURS_PER_SQM * LABOR_COST_PER_HOUR
    
    # Application du facteur de complexité
    total_min = (material_cost_min + labor_cost) * complexity_factor
    total_max = (material_cost_max + labor_cost) * complexity_factor
    
    # Arrondir à l'euro près
    total_min = math.ceil(total_min)
    total_max = math.ceil(total_max)
    
    return {
        'address': address,
        'roof_area_sqm': roof_area,
        'estimated_cost_min': total_min,
        'estimated_cost_max': total_max,
        'material_type': material_type,
        'complexity': complexity,
        'factors': [
            f'Surface de toiture: {roof_area} m²',
            f'Type de couverture recommandé: {material_type.replace("_", " ").title()}',
            f'Complexité: {complexity.title()}',
            'Accessibilité: Bonne'
        ]
    }

@estimation_bp.route('/estimate', methods=['POST'])
def estimate_roof_cost():
    """
    Endpoint pour estimer le coût de rénovation d'une toiture
    """
    try:
        data = request.json
        address = data.get('address')
        
        if not address:
            return jsonify({'error': 'Adresse requise'}), 400
        
        # Pour la démo, on simule l'appel à l'API Google Solar
        # Dans la vraie implémentation, on appellerait l'API Google Solar ici
        estimation = calculate_roof_estimation(address)
        
        return jsonify(estimation), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@estimation_bp.route('/leads', methods=['POST'])
def create_lead():
    """
    Endpoint pour créer un lead (prospect)
    """
    try:
        data = request.json
        
        # Validation des données requises
        required_fields = ['address', 'estimated_cost_min', 'estimated_cost_max']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Champ requis manquant: {field}'}), 400
        
        # Création du lead
        lead = Lead(
            address=data['address'],
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            roof_area_sqm=data.get('roof_area_sqm'),
            estimated_cost_min=data['estimated_cost_min'],
            estimated_cost_max=data['estimated_cost_max'],
            client_name=data.get('client_name'),
            client_email=data.get('client_email'),
            client_phone=data.get('client_phone')
        )
        
        db.session.add(lead)
        db.session.commit()
        
        return jsonify(lead.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@estimation_bp.route('/leads', methods=['GET'])
def get_leads():
    """
    Endpoint pour récupérer tous les leads
    """
    try:
        leads = Lead.query.order_by(Lead.timestamp.desc()).all()
        return jsonify([lead.to_dict() for lead in leads]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@estimation_bp.route('/leads/<int:lead_id>', methods=['GET'])
def get_lead(lead_id):
    """
    Endpoint pour récupérer un lead spécifique
    """
    try:
        lead = Lead.query.get_or_404(lead_id)
        return jsonify(lead.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

