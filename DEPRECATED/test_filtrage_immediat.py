#!/usr/bin/env python3
"""
Test Filtrage Immédiat des Hallucinations
Validation rapide correction artefacts SuperWhisper2
"""

def is_hallucination(text: str) -> bool:
    """
    Détecte les hallucinations communes de Whisper
    """
    if not text or len(text.strip()) == 0:
        return True
        
    text_lower = text.lower().strip()
    
    # Patterns d'hallucination identifiés
    hallucination_patterns = [
        "sous-titres réalisés par la communauté d'amara.org",
        "sous-titres réalisés par l'amara.org", 
        "merci d'avoir regardé cette vidéo",
        "merci d'avoir regardé",
        "n'hésitez pas à vous abonner",
        "like et abonne-toi",
        "commentez et partagez",
        "à bientôt pour une nouvelle vidéo",
        "musique libre de droit",
        "copyright",
        "creative commons"
    ]
    
    # Vérifier patterns exacts
    for pattern in hallucination_patterns:
        if pattern in text_lower:
            return True
            
    # Vérifier répétitions suspectes
    words = text_lower.split()
    if len(words) > 3:
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio < 0.5:  # Plus de 50% de répétitions
            return True
            
    return False

def test_filtrage():
    """Test rapide du filtrage"""
    print("=== TEST FILTRAGE HALLUCINATIONS ===")
    
    # Tests hallucinations (doivent être détectées)
    hallucination_tests = [
        "Sous-titres réalisés par la communauté d'Amara.org",
        "Merci d'avoir regardé cette vidéo!",
        "Merci d'avoir regardé !",
        "N'hésitez pas à vous abonner"
    ]
    
    # Tests textes valides (ne doivent PAS être détectés)
    valid_tests = [
        "Bonjour, ceci est un test de validation",
        "L'intelligence artificielle transforme notre monde",
        "SuperWhisper2 fonctionne avec RTX 3090",
        "Je teste la transcription vocale maintenant"
    ]
    
    print("Tests hallucinations (doivent être DETECTEES):")
    detected = 0
    for i, text in enumerate(hallucination_tests, 1):
        is_hall = is_hallucination(text)
        status = "DETECTE" if is_hall else "MANQUE"
        print(f"  {i}. {status}: '{text[:40]}...'")
        if is_hall:
            detected += 1
    
    print(f"\nHallucinations détectées: {detected}/{len(hallucination_tests)} ({detected/len(hallucination_tests)*100:.1f}%)")
    
    print("\nTests textes valides (doivent être ACCEPTES):")
    accepted = 0
    for i, text in enumerate(valid_tests, 1):
        is_hall = is_hallucination(text)
        status = "ACCEPTE" if not is_hall else "REJETE"
        print(f"  {i}. {status}: '{text[:40]}...'")
        if not is_hall:
            accepted += 1
    
    print(f"\nTextes valides acceptés: {accepted}/{len(valid_tests)} ({accepted/len(valid_tests)*100:.1f}%)")
    
    # Résultat final
    success = (detected >= len(hallucination_tests) * 0.8 and 
               accepted >= len(valid_tests) * 0.95)
    
    print(f"\n=== RESULTAT FINAL ===")
    print(f"STATUS: {'SUCCES' if success else 'ECHEC'}")
    
    if success:
        print("✅ Filtrage opérationnel - Hallucinations seront bloquées")
    else:
        print("❌ Filtrage insuffisant - Ajustements requis")
    
    return success

if __name__ == "__main__":
    test_filtrage() 