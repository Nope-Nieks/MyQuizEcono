import pdfplumber
import re
from typing import List, Dict, Tuple

def extract_questions_from_pdf(pdf_file) -> List[Dict]:
    """
    Extrait les questions d'un fichier PDF en cherchant les patterns comme 'Q1)', 'Q2)', etc.
    Retourne une liste de dictionnaires contenant les questions et leurs réponses.
    """
    questions = []
    current_question = None
    current_answers = []
    
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
                
            # Diviser le texte en lignes
            lines = text.split('\n')
            
            for line in lines:
                # Chercher le pattern de question (Q1), Q2), etc.)
                question_match = re.match(r'Q(\d+)\)\s*(.*)', line.strip())
                
                if question_match:
                    # Si on a une question en cours, on la sauvegarde
                    if current_question:
                        questions.append({
                            'text': current_question,
                            'answers': current_answers
                        })
                    
                    # Commencer une nouvelle question
                    current_question = question_match.group(2)
                    current_answers = []
                else:
                    # Chercher les réponses (A), B), C), D))
                    answer_match = re.match(r'([A-D])\)\s*(.*)', line.strip())
                    if answer_match and current_question:
                        current_answers.append({
                            'text': answer_match.group(2),
                            'is_correct': False  # À déterminer plus tard
                        })
    
    # Ajouter la dernière question
    if current_question:
        questions.append({
            'text': current_question,
            'answers': current_answers
        })
    
    return questions

def extract_questions_from_text(text: str, delimiter: str = '\n') -> List[Dict]:
    """
    Extrait les questions d'un texte en utilisant un délimiteur spécifique.
    """
    questions = []
    current_question = None
    current_answers = []
    
    lines = text.split(delimiter)
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Chercher le pattern de question (Q1), Q2), etc.)
        question_match = re.match(r'Q(\d+)\)\s*(.*)', line)
        
        if question_match:
            # Si on a une question en cours, on la sauvegarde
            if current_question:
                questions.append({
                    'text': current_question,
                    'answers': current_answers
                })
            
            # Commencer une nouvelle question
            current_question = question_match.group(2)
            current_answers = []
        else:
            # Chercher les réponses (A), B), C), D))
            answer_match = re.match(r'([A-D])\)\s*(.*)', line)
            if answer_match and current_question:
                current_answers.append({
                    'text': answer_match.group(2),
                    'is_correct': False  # À déterminer plus tard
                })
    
    # Ajouter la dernière question
    if current_question:
        questions.append({
            'text': current_question,
            'answers': current_answers
        })
    
    return questions 