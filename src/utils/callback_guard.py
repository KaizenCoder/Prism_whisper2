"""
Décorateur de protection pour callbacks Engine V5 SuperWhisper2
Adapte automatiquement les signatures de callbacks pour éviter TypeError

Problème résolu : Engine V5 peut appeler callbacks avec différentes signatures:
- callback(text, timestamp, metadata) 
- callback(text)
- callback(*args, **kwargs)

Solution : Décorateur qui s'adapte automatiquement
"""

import functools
import logging
from typing import Callable, Any

# Configuration du logging pour debug
logger = logging.getLogger(__name__)


def signature_guard(user_callback: Callable[..., Any]) -> Callable[..., Any]:
    """
    Décorateur qui protège un callback utilisateur contre les erreurs de signature.
    
    Usage:
        @signature_guard
        def my_callback(text):
            print(f"Transcription: {text}")
            
        # Fonctionne avec :
        # my_callback("hello")                    ✅
        # my_callback("hello", 12.5, {})         ✅ 
        # my_callback("hello", timestamp=12.5)   ✅
    
    Args:
        user_callback: La fonction callback utilisateur à protéger
        
    Returns:
        Fonction wrapper qui s'adapte aux différentes signatures
    """
    @functools.wraps(user_callback)
    def _signature_adapter(*args, **kwargs):
        """
        Wrapper qui essaie différentes stratégies d'appel selon les arguments reçus
        """
        try:
            # Stratégie 1: Appel direct avec tous les arguments
            return user_callback(*args, **kwargs)
            
        except TypeError as signature_error:
            # Stratégie 2: Si trop d'arguments, on essaie avec seulement le premier (le texte)
            if len(args) >= 1:
                try:
                    logger.debug(f"Callback signature mismatch, trying with text only: {args[0][:50]}...")
                    return user_callback(args[0])
                except TypeError:
                    # Stratégie 3: Si ça ne marche toujours pas, essayer sans arguments
                    try:
                        return user_callback()
                    except TypeError:
                        pass
            
            # Stratégie 4: Essayer seulement les kwargs si il y en a
            if kwargs:
                try:
                    # Chercher la clé 'text' dans les kwargs
                    if 'text' in kwargs:
                        return user_callback(kwargs['text'])
                    # Ou prendre la première valeur
                    elif kwargs:
                        first_value = list(kwargs.values())[0]
                        return user_callback(first_value)
                except TypeError:
                    pass
            
            # Si toutes les stratégies échouent, on log l'erreur et on continue
            logger.warning(f"⚠️ Callback signature incompatible: {signature_error}")
            logger.warning(f"   Args reçus: {len(args)} arguments, {len(kwargs)} kwargs")
            logger.warning(f"   Callback: {user_callback.__name__}")
            
            # On ne lève pas l'exception pour éviter de casser le streaming
            return None
            
    return _signature_adapter


def flexible_callback(callback_func: Callable) -> Callable:
    """
    Alias pour signature_guard - nom plus explicite dans certains contextes
    """
    return signature_guard(callback_func)


# Fonctions utilitaires pour les tests et debugging

def test_callback_compatibility(callback: Callable, test_signatures: list = None) -> dict:
    """
    Teste un callback avec différentes signatures typiques d'Engine V5
    
    Args:
        callback: Fonction callback à tester
        test_signatures: Liste de tuples (args, kwargs) à tester
        
    Returns:
        Dict avec les résultats des tests
    """
    if test_signatures is None:
        test_signatures = [
            # Signatures typiques Engine V5
            (("Hello world",), {}),                          # callback(text)
            (("Hello world", 12.5), {}),                    # callback(text, timestamp) 
            (("Hello world", 12.5, {"confidence": 0.9}), {}), # callback(text, timestamp, metadata)
            ((), {"text": "Hello world"}),                   # callback(text="Hello world")
            ((), {"text": "Hello world", "timestamp": 12.5}), # callback(**kwargs)
        ]
    
    protected_callback = signature_guard(callback)
    results = {}
    
    for i, (args, kwargs) in enumerate(test_signatures):
        try:
            result = protected_callback(*args, **kwargs)
            results[f"test_{i+1}"] = {"success": True, "result": result}
        except Exception as e:
            results[f"test_{i+1}"] = {"success": False, "error": str(e)}
    
    return results


if __name__ == "__main__":
    # Tests du décorateur
    print("🧪 Test du décorateur @signature_guard")
    
    @signature_guard
    def simple_callback(text: str):
        return f"Reçu: '{text}'"
    
    @signature_guard 
    def complex_callback(text: str, timestamp: float = 0.0, metadata: dict = None):
        return f"Text: {text}, Time: {timestamp}, Meta: {metadata}"
    
    # Test des différentes signatures
    test_cases = [
        ("Simple text",),
        ("Text with timestamp", 15.5),
        ("Full signature", 20.0, {"confidence": 0.95}),
    ]
    
    print("\n📝 Test simple_callback:")
    for args in test_cases:
        try:
            result = simple_callback(*args)
            print(f"  ✅ {args} → {result}")
        except Exception as e:
            print(f"  ❌ {args} → ERROR: {e}")
    
    print("\n📝 Test complex_callback:")
    for args in test_cases:
        try:
            result = complex_callback(*args)
            print(f"  ✅ {args} → {result}")
        except Exception as e:
            print(f"  ❌ {args} → ERROR: {e}")
    
    print("\n🎯 Tests automatisés:")
    results = test_callback_compatibility(simple_callback)
    for test_name, result in results.items():
        status = "✅" if result["success"] else "❌"
        print(f"  {status} {test_name}: {result}") 