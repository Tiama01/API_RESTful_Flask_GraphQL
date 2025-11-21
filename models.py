"""
Modèles de données pour l'application
Utilise SQLite pour stocker les articles
"""
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Configuration de la base de données
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///articles.db')

# Création du moteur SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False)

# Base pour les modèles
Base = declarative_base()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Article(Base):
    """
    Modèle Article pour la base de données
    """
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)

    def to_dict(self):
        """
        Convertit l'article en dictionnaire
        """
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content
        }

    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title}')>"


def init_db():
    """
    Initialise la base de données en créant les tables
    """
    Base.metadata.create_all(bind=engine)
    print("Base de donnees initialisee avec succes")


def get_db():
    """
    Obtient une session de base de données
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

