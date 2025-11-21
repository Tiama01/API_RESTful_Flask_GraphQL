"""
API RESTful Flask pour la gestion d'articles de blog
Inclut le monitoring Prometheus
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
from models import init_db, get_db, Article
from sqlalchemy.orm import Session
import os

# Initialisation de l'application Flask
app = Flask(__name__)
CORS(app)  # Permet les requêtes cross-origin

# Configuration Prometheus
metrics = PrometheusMetrics(app)

# Initialisation de la base de données
init_db()

# Note: PrometheusMetrics expose automatiquement les métriques suivantes :
# - flask_http_request_total : Nombre total de requêtes HTTP (avec labels method, status)
# - flask_http_request_duration_seconds : Temps de réponse par endpoint (avec labels method, path, status)
# - flask_http_request_exceptions_total : Nombre d'exceptions
# Ces métriques sont déjà suffisantes pour le monitoring


@app.route('/', methods=['GET'])
def index():
    """
    Endpoint racine - Affiche les informations de l'API
    """
    base_url = request.url_root.rstrip('/')
    return jsonify({
        'service': 'API RESTful Flask - Gestion d\'articles de blog',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': f'{base_url}/health',
            'articles': {
                'list': {
                    'url': f'{base_url}/articles',
                    'method': 'GET',
                    'description': 'Récupère tous les articles'
                },
                'get': {
                    'url': f'{base_url}/articles/{{id}}',
                    'method': 'GET',
                    'description': 'Récupère un article par ID'
                },
                'create': {
                    'url': f'{base_url}/articles',
                    'method': 'POST',
                    'description': 'Crée un nouvel article',
                    'body': {
                        'title': 'string (requis)',
                        'content': 'string (requis)'
                    }
                },
                'update': {
                    'url': f'{base_url}/articles/{{id}}',
                    'method': 'PUT',
                    'description': 'Met à jour un article',
                    'body': {
                        'title': 'string (optionnel)',
                        'content': 'string (optionnel)'
                    }
                },
                'delete': {
                    'url': f'{base_url}/articles/{{id}}',
                    'method': 'DELETE',
                    'description': 'Supprime un article'
                }
            },
            'metrics': {
                'url': f'{base_url}/metrics',
                'method': 'GET',
                'description': 'Métriques Prometheus'
            }
        },
        'documentation': 'Consultez le README.md pour plus d\'informations'
    }), 200


@app.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de santé pour vérifier que l'API fonctionne
    """
    return jsonify({'status': 'healthy', 'service': 'Flask REST API'}), 200


@app.route('/articles', methods=['GET'])
def get_articles():
    """
    GET /articles
    Récupère tous les articles
    """
    try:
        db: Session = next(get_db())
        articles = db.query(Article).all()
        result = [article.to_dict() for article in articles]
        db.close()
        return jsonify({
            'success': True,
            'data': result,
            'count': len(result)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    """
    GET /articles/{id}
    Récupère un article par son ID
    """
    try:
        db: Session = next(get_db())
        article = db.query(Article).filter(Article.id == article_id).first()
        db.close()

        if not article:
            return jsonify({
                'success': False,
                'error': 'Article non trouvé'
            }), 404

        return jsonify({
            'success': True,
            'data': article.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/articles', methods=['POST'])
def create_article():
    """
    POST /articles
    Crée un nouvel article
    Body: { "title": "...", "content": "..." }
    """
    try:
        data = request.get_json()

        # Validation des données
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({
                'success': False,
                'error': 'Les champs "title" et "content" sont requis'
            }), 400

        if not data['title'] or not data['content']:
            return jsonify({
                'success': False,
                'error': 'Les champs "title" et "content" ne peuvent pas être vides'
            }), 400

        db: Session = next(get_db())
        new_article = Article(
            title=data['title'],
            content=data['content']
        )
        db.add(new_article)
        db.commit()
        db.refresh(new_article)
        article_dict = new_article.to_dict()
        db.close()

        return jsonify({
            'success': True,
            'data': article_dict,
            'message': 'Article créé avec succès'
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/articles/<int:article_id>', methods=['PUT'])
def update_article(article_id):
    """
    PUT /articles/{id}
    Met à jour un article existant
    Body: { "title": "...", "content": "..." }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Données de mise à jour requises'
            }), 400

        db: Session = next(get_db())
        article = db.query(Article).filter(Article.id == article_id).first()

        if not article:
            db.close()
            return jsonify({
                'success': False,
                'error': 'Article non trouvé'
            }), 404

        # Mise à jour des champs fournis
        if 'title' in data:
            article.title = data['title']
        if 'content' in data:
            article.content = data['content']

        db.commit()
        db.refresh(article)
        article_dict = article.to_dict()
        db.close()

        return jsonify({
            'success': True,
            'data': article_dict,
            'message': 'Article mis à jour avec succès'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/articles/<int:article_id>', methods=['DELETE'])
def delete_article(article_id):
    """
    DELETE /articles/{id}
    Supprime un article
    """
    try:
        db: Session = next(get_db())
        article = db.query(Article).filter(Article.id == article_id).first()

        if not article:
            db.close()
            return jsonify({
                'success': False,
                'error': 'Article non trouvé'
            }), 404

        db.delete(article)
        db.commit()
        db.close()

        return jsonify({
            'success': True,
            'message': f'Article {article_id} supprimé avec succès'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/metrics', methods=['GET'])
def metrics_endpoint():
    """
    Endpoint pour les métriques Prometheus
    Expose les métriques au format Prometheus
    """
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from flask import Response
    return Response(
        generate_latest(metrics.registry),
        mimetype=CONTENT_TYPE_LATEST
    )


@app.errorhandler(404)
def not_found(error):
    """
    Gestionnaire d'erreur 404
    """
    return jsonify({
        'success': False,
        'error': 'Endpoint non trouvé'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """
    Gestionnaire d'erreur 500
    """
    return jsonify({
        'success': False,
        'error': 'Erreur interne du serveur'
    }), 500


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    print(f"Demarrage de l'API REST Flask sur http://{host}:{port}")
    print(f"Metriques Prometheus disponibles sur http://{host}:{port}/metrics")
    print(f"Health check disponible sur http://{host}:{port}/health")

    app.run(host=host, port=port, debug=debug)

