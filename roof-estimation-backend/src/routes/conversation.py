from flask import Blueprint, jsonify, request
from src.models.conversation import ConversationSession
from src.models.user import db
import uuid
import random
import math

conversation_bp = Blueprint('conversation', __name__)

# Questions du moteur de conversation
CONVERSATION_QUESTIONS = {
    'roof_type': {
        'id': 'roof_type',
        'question': 'Quel est le type de votre toiture actuelle ?',
        'type': 'choice',
        'options': [
            {'value': 'tuiles_terre_cuite', 'label': 'Tuiles en terre cuite'},
            {'value': 'tuiles_beton', 'label': 'Tuiles en béton'},
            {'value': 'ardoise', 'label': 'Ardoise'},
            {'value': 'zinc', 'label': 'Zinc'},
            {'value': 'bac_acier', 'label': 'Bac acier'},
            {'value': 'autre', 'label': 'Autre / Je ne sais pas'}
        ],
        'next_question': 'roof_condition'
    },
    'roof_condition': {
        'id': 'roof_condition',
        'question': 'Quel est l\'état général de votre toiture ?',
        'type': 'choice',
        'options': [
            {'value': 'neuve', 'label': 'Neuve (moins de 5 ans)'},
            {'value': 'bon_etat', 'label': 'Bon état (5-15 ans)'},
            {'value': 'usee', 'label': 'Usée (15-30 ans)'},
            {'value': 'endommagee', 'label': 'Endommagée (fuites, tuiles cassées)'}
        ],
        'next_question': 'roof_elements'
    },
    'roof_elements': {
        'id': 'roof_elements',
        'question': 'Y a-t-il des éléments spécifiques sur votre toiture ?',
        'type': 'multiple_choice',
        'options': [
            {'value': 'cheminee', 'label': 'Cheminée(s)'},
            {'value': 'lucarne', 'label': 'Lucarne(s)'},
            {'value': 'fenetre_toit', 'label': 'Fenêtre(s) de toit'},
            {'value': 'panneaux_solaires', 'label': 'Panneaux solaires'},
            {'value': 'antenne', 'label': 'Antenne/Parabole'},
            {'value': 'aucun', 'label': 'Aucun élément particulier'}
        ],
        'next_question': 'roof_access'
    },
    'roof_access': {
        'id': 'roof_access',
        'question': 'Comment évaluez-vous l\'accès à votre toiture ?',
        'type': 'choice',
        'options': [
            {'value': 'facile', 'label': 'Facile (maison plain-pied, bon accès)'},
            {'value': 'moyen', 'label': 'Moyen (étage, quelques contraintes)'},
            {'value': 'difficile', 'label': 'Difficile (hauteur importante, accès restreint)'}
        ],
        'next_question': 'material_preference'
    },
    'material_preference': {
        'id': 'material_preference',
        'question': 'Avez-vous une préférence pour le type de matériau ?',
        'type': 'choice',
        'options': [
            {'value': 'identique', 'label': 'Identique à l\'existant'},
            {'value': 'amelioration', 'label': 'Amélioration (meilleure qualité)'},
            {'value': 'economique', 'label': 'Solution économique'},
            {'value': 'ecologique', 'label': 'Solution écologique'},
            {'value': 'pas_preference', 'label': 'Pas de préférence particulière'}
        ],
        'next_question': 'insulation'
    },
    'insulation': {
        'id': 'insulation',
        'question': 'Souhaitez-vous améliorer l\'isolation de votre toiture ?',
        'type': 'choice',
        'options': [
            {'value': 'oui_complete', 'label': 'Oui, isolation complète'},
            {'value': 'oui_partielle', 'label': 'Oui, amélioration partielle'},
            {'value': 'non', 'label': 'Non, pas d\'isolation'},
            {'value': 'pas_sur', 'label': 'Je ne sais pas / À voir'}
        ],
        'next_question': None  # Dernière question
    }
}

# Données de coûts mises à jour
MATERIAL_COSTS = {
    'tuiles_terre_cuite': {'min': 25, 'max': 90, 'quality_factor': 1.0},
    'tuiles_beton': {'min': 35, 'max': 45, 'quality_factor': 0.8},
    'bac_acier': {'min': 15, 'max': 35, 'quality_factor': 0.6},
    'zinc': {'min': 40, 'max': 90, 'quality_factor': 1.2},
    'ardoise': {'min': 60, 'max': 100, 'quality_factor': 1.4},
    'autre': {'min': 30, 'max': 70, 'quality_factor': 1.0}
}

CONDITION_FACTORS = {
    'neuve': 0.8,  # Moins de travaux
    'bon_etat': 1.0,  # Standard
    'usee': 1.2,  # Plus de préparation
    'endommagee': 1.5  # Réparations importantes
}

ACCESS_FACTORS = {
    'facile': 1.0,
    'moyen': 1.2,
    'difficile': 1.5
}

INSULATION_COSTS = {
    'oui_complete': {'min': 20, 'max': 40},  # €/m² supplémentaire
    'oui_partielle': {'min': 10, 'max': 25},
    'non': {'min': 0, 'max': 0},
    'pas_sur': {'min': 5, 'max': 15}  # Estimation moyenne
}

def calculate_refined_estimation(session):
    """Calcule une estimation affinée basée sur les réponses de la conversation"""
    conversation_data = session.get_conversation_data()
    roof_area = session.roof_area_sqm or random.randint(80, 180)
    
    # Coût de base selon le matériau
    roof_type = conversation_data.get('roof_type', 'tuiles_terre_cuite')
    material_costs = MATERIAL_COSTS.get(roof_type, MATERIAL_COSTS['tuiles_terre_cuite'])
    
    base_cost_min = roof_area * material_costs['min']
    base_cost_max = roof_area * material_costs['max']
    
    # Facteur d'état de la toiture
    condition = conversation_data.get('roof_condition', 'bon_etat')
    condition_factor = CONDITION_FACTORS.get(condition, 1.0)
    
    # Facteur d'accès
    access = conversation_data.get('roof_access', 'moyen')
    access_factor = ACCESS_FACTORS.get(access, 1.2)
    
    # Coût de la main d'œuvre
    labor_hours_per_sqm = 0.5 * condition_factor * access_factor
    labor_cost = roof_area * labor_hours_per_sqm * 50  # 50€/heure
    
    # Coût d'isolation
    insulation = conversation_data.get('insulation', 'non')
    insulation_costs = INSULATION_COSTS.get(insulation, INSULATION_COSTS['non'])
    insulation_cost_min = roof_area * insulation_costs['min']
    insulation_cost_max = roof_area * insulation_costs['max']
    
    # Facteur de complexité selon les éléments de toiture
    elements = conversation_data.get('roof_elements', [])
    complexity_factor = 1.0
    if isinstance(elements, list):
        if 'cheminee' in elements:
            complexity_factor += 0.1
        if 'lucarne' in elements:
            complexity_factor += 0.15
        if 'fenetre_toit' in elements:
            complexity_factor += 0.1
        if 'panneaux_solaires' in elements:
            complexity_factor += 0.2
    
    # Calcul final
    total_min = (base_cost_min + labor_cost + insulation_cost_min) * complexity_factor
    total_max = (base_cost_max + labor_cost + insulation_cost_max) * complexity_factor
    
    # Ajustement selon la préférence matériau
    material_pref = conversation_data.get('material_preference', 'identique')
    if material_pref == 'amelioration':
        total_min *= 1.2
        total_max *= 1.4
    elif material_pref == 'economique':
        total_min *= 0.8
        total_max *= 1.0
    elif material_pref == 'ecologique':
        total_min *= 1.1
        total_max *= 1.3
    
    return math.ceil(total_min), math.ceil(total_max)

@conversation_bp.route('/start', methods=['POST'])
def start_conversation():
    """Démarre une nouvelle session de conversation"""
    try:
        data = request.json
        address = data.get('address')
        
        if not address:
            return jsonify({'error': 'Adresse requise'}), 400
        
        # Créer une nouvelle session
        session_id = str(uuid.uuid4())
        session = ConversationSession(
            id=session_id,
            address=address,
            current_question_id='roof_type',
            conversation_data='{}'
        )
        
        # Simuler les données de toiture (dans la vraie version, utiliser Google Solar API)
        session.roof_area_sqm = random.randint(80, 180)
        session.latitude = 48.8566 + random.uniform(-0.1, 0.1)  # Paris approximatif
        session.longitude = 2.3522 + random.uniform(-0.1, 0.1)
        
        db.session.add(session)
        db.session.commit()
        
        # Retourner la première question
        first_question = CONVERSATION_QUESTIONS['roof_type']
        
        return jsonify({
            'session_id': session_id,
            'address': address,
            'roof_area_sqm': session.roof_area_sqm,
            'question': first_question,
            'progress': 1,
            'total_questions': len(CONVERSATION_QUESTIONS)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@conversation_bp.route('/answer', methods=['POST'])
def answer_question():
    """Traite une réponse et retourne la question suivante ou l'estimation finale"""
    try:
        data = request.json
        session_id = data.get('session_id')
        answer = data.get('answer')
        
        if not session_id or not answer:
            return jsonify({'error': 'session_id et answer requis'}), 400
        
        # Récupérer la session
        session = ConversationSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session non trouvée'}), 404
        
        # Mettre à jour les données de conversation
        conversation_data = session.get_conversation_data()
        current_question_id = session.current_question_id
        
        if current_question_id:
            conversation_data[current_question_id] = answer
            session.set_conversation_data(conversation_data)
        
        # Déterminer la question suivante
        current_question = CONVERSATION_QUESTIONS.get(current_question_id)
        next_question_id = current_question.get('next_question') if current_question else None
        
        if next_question_id:
            # Il y a une question suivante
            session.current_question_id = next_question_id
            next_question = CONVERSATION_QUESTIONS[next_question_id]
            
            # Calculer l'estimation intermédiaire
            cost_min, cost_max = calculate_refined_estimation(session)
            session.estimated_cost_min = cost_min
            session.estimated_cost_max = cost_max
            
            db.session.commit()
            
            # Calculer le progrès
            questions_answered = len([q for q in CONVERSATION_QUESTIONS.keys() if q in conversation_data])
            progress = questions_answered + 1
            
            return jsonify({
                'session_id': session_id,
                'question': next_question,
                'progress': progress,
                'total_questions': len(CONVERSATION_QUESTIONS),
                'intermediate_estimation': {
                    'min': cost_min,
                    'max': cost_max
                }
            }), 200
        else:
            # Conversation terminée, calculer l'estimation finale
            cost_min, cost_max = calculate_refined_estimation(session)
            session.estimated_cost_min = cost_min
            session.estimated_cost_max = cost_max
            session.is_completed = True
            session.current_question_id = None
            
            db.session.commit()
            
            return jsonify({
                'session_id': session_id,
                'completed': True,
                'final_estimation': {
                    'address': session.address,
                    'roof_area_sqm': session.roof_area_sqm,
                    'estimated_cost_min': cost_min,
                    'estimated_cost_max': cost_max,
                    'conversation_summary': conversation_data
                }
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@conversation_bp.route('/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Récupère l'état d'une session de conversation"""
    try:
        session = ConversationSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session non trouvée'}), 404
        
        return jsonify(session.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@conversation_bp.route('/sessions', methods=['GET'])
def get_sessions():
    """Récupère toutes les sessions de conversation"""
    try:
        sessions = ConversationSession.query.order_by(ConversationSession.timestamp.desc()).all()
        return jsonify([session.to_dict() for session in sessions]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

