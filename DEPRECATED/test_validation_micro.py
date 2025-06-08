#!/usr/bin/env python3
"""
Test Validation Microphone - SuperWhisper2 Engine V5
Test terrain avec texte de validation complexe
RTX 3090 UNIQUEMENT - Performance <1s
"""

import os
import sys
import time
import threading
import queue
from typing import Optional

# Configuration RTX 3090 OBLIGATOIRE
os.environ['CUDA_VISIBLE_DEVICES'] = '1'  # RTX 3090 24GB
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'

# Ajouter src au path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Texte de validation fourni par l'utilisateur
TEXTE_VALIDATION = """Bonjour, ceci est un test de validation pour SuperWhisper2. Je vais maintenant 
énoncerplusieurs phrases de complexité croissante pour évaluer la précision de transcription.
Premièrement, des mots simples : chat, chien, maison, voiture, ordinateur, téléphone.
Deuxièmement, des phrases courtes : Il fait beau aujourd'hui. Le café est délicieux. J'aime la musique classique.
Troisièmement, des phrases plus complexes : L'intelligence artificielle transforme notre manière de travailler 
et de communiquer dans le monde moderne.
Quatrièmement, des termes techniques : algorithme, machine learning, GPU RTX 3090, faster-whisper, quantification INT8, 
latence de transcription.
Cinquièmement, des nombres et dates : vingt-trois, quarante-sept, mille neuf cent quatre-vingt-quinze, 
le quinze janvier deux mille vingt-quatre.
Sixièmement, des mots difficiles : chrysanthème, anticonstitutionnellement, prestidigitateur, kakémono, yaourt.
Septièmement, une phrase longue et complexe : L'optimisation des performances de transcription vocale nécessite 
une approche méthodique combinant la sélection appropriée des modèles, l'ajustement des paramètres de traitement,
 et l'implémentation d'algorithmes de post-traitement pour améliorer la qualité du résultat final.
Fin du test de validation."""

class ValidationMicrophone:
    """Test validation microphone avec Engine V5"""
    
    def __init__(self):
        self.engine = None
        self.transcriptions = []
        self.result_queue = queue.Queue()
        self.listening = False
        
    def setup_engine(self) -> bool:
        """Initialise SuperWhisper2EngineV5"""
        try:
            print("📦 Chargement SuperWhisper2EngineV5...")
            from core.whisper_engine_v5 import SuperWhisper2EngineV5
            
            self.engine = SuperWhisper2EngineV5()
            
            # Callback pour capturer transcriptions
            def on_transcription(text: str):
                if text and text.strip():
                    timestamp = time.time()
                    self.result_queue.put((timestamp, text.strip()))
                    print(f"📝 Transcription reçue: {text[:80]}...")
            
            self.engine.set_transcription_callback(on_transcription)
            
            print("🔥 Démarrage Engine V5...")
            success = self.engine.start_engine()
            
            if success:
                print("✅ Engine V5 démarré avec succès!")
                
                # Afficher status
                status = self.engine.get_phase3_status()
                print(f"⚡ Optimisations: {status['optimizations_count']}/{status['total_optimizations']}")
                print(f"🎮 GPU VRAM: {status['gpu_status']['vram_cache_gb']:.1f}GB")
                print(f"🔀 CUDA Streams: {status['gpu_status']['cuda_streams']}")
                return True
            else:
                print("❌ Échec démarrage Engine V5")
                return False
                
        except Exception as e:
            print(f"❌ Erreur setup engine: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def afficher_texte_validation(self):
        """Affiche le texte à lire"""
        print("\n" + "="*80)
        print("📖 TEXTE À LIRE AU MICROPHONE")
        print("="*80)
        print()
        
        # Découper en sections pour faciliter la lecture
        sections = TEXTE_VALIDATION.split('\n')
        for i, section in enumerate(sections, 1):
            if section.strip():
                print(f"{i:2d}. {section.strip()}")
                print()
        
        print("="*80)
        print()
    
    def demarrer_ecoute(self):
        """Démarre l'écoute continue"""
        self.listening = True
        print("🎤 ÉCOUTE ACTIVE - Commencez à lire le texte...")
        print("💡 Appuyez sur Ctrl+C pour arrêter\n")
        
        start_time = time.time()
        
        try:
            while self.listening:
                try:
                    # Vérifier nouvelles transcriptions
                    while not self.result_queue.empty():
                        timestamp, text = self.result_queue.get_nowait()
                        latency = timestamp - start_time if start_time else 0
                        
                        self.transcriptions.append({
                            'timestamp': timestamp,
                            'latency': latency,
                            'text': text
                        })
                        
                        print(f"⏱️ [{latency:.1f}s] {text}")
                    
                    time.sleep(0.1)  # Éviter surcharge CPU
                    
                except queue.Empty:
                    continue
                    
        except KeyboardInterrupt:
            print("\n🛑 Arrêt demandé par l'utilisateur")
            self.listening = False
    
    def analyser_resultats(self):
        """Analyse les résultats de validation"""
        if not self.transcriptions:
            print("❌ Aucune transcription capturée")
            return
        
        print("\n" + "="*80)
        print("📊 ANALYSE DES RÉSULTATS")
        print("="*80)
        
        # Concaténer toutes les transcriptions
        texte_complet = " ".join([t['text'] for t in self.transcriptions])
        
        print(f"📝 Nombre de segments: {len(self.transcriptions)}")
        print(f"📏 Longueur totale: {len(texte_complet)} caractères")
        print(f"⏱️ Durée totale: {self.transcriptions[-1]['timestamp'] - self.transcriptions[0]['timestamp']:.1f}s")
        
        print("\n🔍 TRANSCRIPTION COMPLÈTE:")
        print("-" * 40)
        print(texte_complet)
        print("-" * 40)
        
        # Analyse de précision simple (mots clés)
        mots_cles = [
            "SuperWhisper2", "validation", "complexité", "précision",
            "chat", "chien", "maison", "voiture", "ordinateur", "téléphone",
            "intelligence artificielle", "algorithme", "machine learning",
            "RTX 3090", "faster-whisper", "quantification", "INT8",
            "chrysanthème", "anticonstitutionnellement", "prestidigitateur"
        ]
        
        mots_trouves = 0
        for mot in mots_cles:
            if mot.lower() in texte_complet.lower():
                mots_trouves += 1
        
        precision_mots = (mots_trouves / len(mots_cles)) * 100
        
        print(f"\n📊 MÉTRIQUES:")
        print(f"✅ Mots-clés trouvés: {mots_trouves}/{len(mots_cles)} ({precision_mots:.1f}%)")
        
        # Analyse latence (si disponible)
        if len(self.transcriptions) > 1:
            latences = [t['latency'] for t in self.transcriptions[1:]]  # Ignorer première
            if latences:
                latence_moyenne = sum(latences) / len(latences)
                latence_min = min(latences)
                latence_max = max(latences)
                
                print(f"⏱️ Latence moyenne: {latence_moyenne:.2f}s")
                print(f"⚡ Latence minimale: {latence_min:.2f}s")
                print(f"🐌 Latence maximale: {latence_max:.2f}s")
                
                if latence_moyenne < 1.0:
                    print("🏆 OBJECTIF <1s ATTEINT!")
                elif latence_moyenne < 3.0:
                    print("✅ OBJECTIF PHASE 3 VALIDÉ (<3s)")
                else:
                    print("⚠️ Latence élevée à optimiser")
    
    def cleanup(self):
        """Nettoyage ressources"""
        self.listening = False
        if self.engine:
            try:
                self.engine.stop_engine()
                print("✅ Engine arrêté proprement")
            except:
                pass

def main():
    """Test principal validation microphone"""
    
    print("🎤 TEST VALIDATION MICROPHONE - SUPERWHISPER2 ENGINE V5")
    print("=" * 60)
    print("📋 RÈGLES: RTX 3090 UNIQUEMENT - Performance <1s attendue")
    print()
    
    validator = ValidationMicrophone()
    
    try:
        # Setup Engine V5
        if not validator.setup_engine():
            print("❌ Impossible de démarrer Engine V5")
            return False
        
        # Afficher texte à lire
        validator.afficher_texte_validation()
        
        # Attendre confirmation utilisateur
        input("📢 Appuyez sur ENTRÉE quand vous êtes prêt à commencer la lecture...")
        print()
        
        # Démarrer écoute
        validator.demarrer_ecoute()
        
        # Analyser résultats
        validator.analyser_resultats()
        
        return True
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrompu")
        return False
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        validator.cleanup()

if __name__ == "__main__":
    success = main()
    print(f"\n🎯 VALIDATION: {'SUCCÈS' if success else 'ÉCHEC'}")
    sys.exit(0 if success else 1) 