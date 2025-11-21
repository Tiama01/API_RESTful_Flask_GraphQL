"""
Resolvers GraphQL
Chaque resolver appelle l'API REST Flask
"""
import requests
import os
from typing import Dict, Any, Optional

# URL de l'API REST Flask
REST_API_URL = os.getenv('REST_API_URL', 'http://localhost:5000')


def make_rest_request(method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Effectue une requête HTTP vers l'API REST
    
    Args:
        method: Méthode HTTP (GET, POST, PUT, DELETE)
        endpoint: Endpoint de l'API
        data: Données à envoyer (optionnel)
    
    Returns:
        Réponse JSON de l'API
    """
    url = f"{REST_API_URL}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=5)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=5)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers, timeout=5)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=5)
        else:
            return {'success': False, 'error': f'Méthode {method} non supportée'}
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f'Erreur lors de la communication avec l\'API REST: {str(e)}'
        }


def resolve_get_articles(*_):
    """
    Resolver pour la query getArticles
    Récupère tous les articles depuis l'API REST
    """
    result = make_rest_request('GET', '/articles')
    
    if not result.get('success'):
        return {
            'success': False,
            'data': [],
            'count': 0
        }
    
    return {
        'success': True,
        'data': result.get('data', []),
        'count': result.get('count', 0)
    }


def resolve_get_article(*_, id: int):
    """
    Resolver pour la query getArticle
    Récupère un article par ID depuis l'API REST
    """
    result = make_rest_request('GET', f'/articles/{id}')
    return result


def resolve_create_article(*_, title: str, content: str):
    """
    Resolver pour la mutation createArticle
    Crée un nouvel article via l'API REST
    """
    data = {
        'title': title,
        'content': content
    }
    result = make_rest_request('POST', '/articles', data)
    return result


def resolve_update_article(*_, id: int, title: Optional[str] = None, content: Optional[str] = None):
    """
    Resolver pour la mutation updateArticle
    Met à jour un article via l'API REST
    """
    data = {}
    if title is not None:
        data['title'] = title
    if content is not None:
        data['content'] = content
    
    if not data:
        return {
            'success': False,
            'error': 'Au moins un champ (title ou content) doit être fourni'
        }
    
    result = make_rest_request('PUT', f'/articles/{id}', data)
    return result


def resolve_delete_article(*_, id: int):
    """
    Resolver pour la mutation deleteArticle
    Supprime un article via l'API REST
    """
    result = make_rest_request('DELETE', f'/articles/{id}')
    
    if result.get('success'):
        return {
            'success': True,
            'message': result.get('message', f'Article {id} supprimé avec succès')
        }
    else:
        return {
            'success': False,
            'message': result.get('error', 'Erreur lors de la suppression')
        }

