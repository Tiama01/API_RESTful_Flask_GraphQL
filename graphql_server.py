"""
Serveur GraphQL utilisant Ariadne
Consomme l'API REST Flask pour récupérer et modifier les données
"""
from ariadne import make_executable_schema, graphql_sync, QueryType, MutationType
from ariadne.explorer.playground import PLAYGROUND_HTML
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from graphql_schema import type_defs
from graphql_resolvers import (
    resolve_get_articles,
    resolve_get_article,
    resolve_create_article,
    resolve_update_article,
    resolve_delete_article
)

# Initialisation de l'application Flask pour GraphQL
app = Flask(__name__)
CORS(app)

# Création des types Query et Mutation avec les resolvers
query = QueryType()
query.set_field("getArticles", resolve_get_articles)
query.set_field("getArticle", resolve_get_article)

mutation = MutationType()
mutation.set_field("createArticle", resolve_create_article)
mutation.set_field("updateArticle", resolve_update_article)
mutation.set_field("deleteArticle", resolve_delete_article)

# Création du schéma exécutable avec les resolvers
schema = make_executable_schema(type_defs, query, mutation)


@app.route('/graphql', methods=['GET'])
def graphql_playground_route():
    """
    Interface GraphQL Playground pour tester les requêtes
    """
    from flask import Response
    
    # Obtenir l'URL de base pour l'endpoint GraphQL
    graphql_endpoint = f"{request.url_root.rstrip('/')}/graphql"
    
    # Remplacer toutes les occurrences de {{ title }} dans le HTML
    playground_html = PLAYGROUND_HTML.replace('{{ title }}', 'GraphQL Playground - Articles API')
    
    # Remplacer les variables Jinja2 et configurer l'endpoint
    # Remplacer {% if settings %}settings: {% raw settings  %},{% endif %} par la configuration
    import re
    settings_pattern = r'\{% if settings %}settings: \{% raw settings  %\},\{% endif %\}'
    endpoint_config = f"endpoint: '{graphql_endpoint}'"
    playground_html = re.sub(settings_pattern, endpoint_config, playground_html)
    
    return Response(
        playground_html,
        mimetype='text/html',
        headers={
            'Content-Type': 'text/html; charset=utf-8'
        }
    ), 200


@app.route('/graphql', methods=['POST'])
def graphql_server():
    """
    Endpoint GraphQL principal
    Traite les requêtes GraphQL et appelle les resolvers
    """
    try:
        data = request.get_json()
        
        # Exécution de la requête GraphQL
        success, result = graphql_sync(
            schema,
            data,
            context_value=request,
            debug=app.debug
        )
        
        status_code = 200 if success else 400
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            'errors': [{'message': str(e)}]
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de santé pour vérifier que le serveur GraphQL fonctionne
    """
    return jsonify({
        'status': 'healthy',
        'service': 'GraphQL Server',
        'rest_api_url': os.getenv('REST_API_URL', 'http://localhost:5000')
    }), 200


if __name__ == '__main__':
    port = int(os.getenv('GRAPHQL_PORT', 8000))
    host = os.getenv('GRAPHQL_HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    rest_api_url = os.getenv('REST_API_URL', 'http://localhost:5000')
    
    print(f"Demarrage du serveur GraphQL sur http://{host}:{port}")
    print(f"GraphQL Playground disponible sur http://{host}:{port}/graphql")
    print(f"API REST cible: {rest_api_url}")
    print(f"Health check disponible sur http://{host}:{port}/health")
    print("\nAssurez-vous que l'API REST Flask est demarree sur le port 5000")
    
    app.run(host=host, port=port, debug=debug)

