"""
Schéma GraphQL pour les articles
Définit les types, queries et mutations
"""
from ariadne import gql

# Schéma GraphQL
type_defs = gql("""
    type Article {
        id: Int!
        title: String!
        content: String!
    }

    type ArticleResponse {
        success: Boolean!
        data: Article
        message: String
    }

    type ArticlesResponse {
        success: Boolean!
        data: [Article!]!
        count: Int!
    }

    type DeleteResponse {
        success: Boolean!
        message: String!
    }

    type Query {
        # Récupère tous les articles
        getArticles: ArticlesResponse!
        
        # Récupère un article par ID
        getArticle(id: Int!): ArticleResponse!
    }

    type Mutation {
        # Crée un nouvel article
        createArticle(title: String!, content: String!): ArticleResponse!
        
        # Met à jour un article existant
        updateArticle(id: Int!, title: String, content: String): ArticleResponse!
        
        # Supprime un article
        deleteArticle(id: Int!): DeleteResponse!
    }
""")

