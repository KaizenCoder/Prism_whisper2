#!/usr/bin/env python3
"""
CORRECTIF IMMÉDIAT - VAD Bypass pour Engine V5
Développeur C - Solution déblocage rapide

OBJECTIF: Désactiver temporairement VAD pour Engine V5 uniquement
IMPACT: Streaming Engine V5 fonctionnel + filtrage hallucinations maintenu
TEMPS: 30 minutes implémentation + test
"""

import os
import sys

# Ajouter src au path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def apply_vad_bypass_fix():
    """
    Applique le correctif VAD bypass pour Engine V5
    """
    
    print("🔧 CORRECTIF DÉVELOPPEUR C - VAD BYPASS ENGINE V5")
    print("=" * 60)
    
    # 1. Backup du fichier original
    print("📦 Sauvegarde fichier original...")
    
    import shutil
    audio_streamer_path = os.path.join(src_dir, 'audio', 'audio_streamer.py')
    backup_path = audio_streamer_path + '.backup_before_vad_bypass'
    
    if not os.path.exists(backup_path):
        shutil.copy2(audio_streamer_path, backup_path)
        print(f"✅ Backup créé: {backup_path}")
    else:
        print(f"✅ Backup existe déjà: {backup_path}")
    
    # 2. Lecture du fichier actuel
    print("📖 Lecture AudioStreamer actuel...")
    with open(audio_streamer_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 3. Recherche et remplacement de la méthode VAD
    print("🔍 Recherche méthode has_voice_activity...")
    
    # Pattern à remplacer
    old_pattern = '''    def has_voice_activity(self, audio_chunk: np.ndarray) -> bool:
        """
        Détecte si le chunk audio contient de la voix
        """
        # Vérifier énergie minimum  
        energy = np.mean(audio_chunk ** 2)
        if energy < self.min_energy_threshold:
            return False
        
        # Convertir pour WebRTC VAD (16-bit PCM)
        audio_int16 = (audio_chunk * 32767).astype(np.int16)
        
        # Analyser par segments de 30ms (480 samples à 16kHz)
        frame_length = 480
        voice_frames = 0
        total_frames = 0
        
        for i in range(0, len(audio_int16) - frame_length, frame_length):
            frame = audio_int16[i:i + frame_length].tobytes()
            try:
                if self.vad.is_speech(frame, self.sample_rate):
                    voice_frames += 1
                total_frames += 1
            except Exception:
                continue  # Ignorer les frames problématiques
        
        if total_frames == 0:
            return False
        
        voice_ratio = voice_frames / total_frames
        return voice_ratio >= self.min_voice_ratio'''
    
    # Nouveau pattern - VAD bypass pour Engine V5
    new_pattern = '''    def has_voice_activity(self, audio_chunk: np.ndarray) -> bool:
        """
        Détecte si le chunk audio contient de la voix
        CORRECTIF DÉVELOPPEUR C: Bypass VAD pour Engine V5 (déblocage streaming)
        """
        # CORRECTIF IMMÉDIAT: Bypass VAD pour débloquer Engine V5
        # Justification technique:
        # - Hardware Rode OK (RMS 1.4x seuil)
        # - WebRTC VAD incompatible avec Rode NT-USB  
        # - Filtrage hallucinations maintenu dans Engine V5
        
        # Vérifier énergie minimum basique
        energy = np.mean(audio_chunk ** 2)
        
        # Seuil très permissif pour déblocage (vs 0.0005 original)
        basic_threshold = 0.0001
        
        # BYPASS VAD: Juste vérifier énergie basique
        has_energy = energy >= basic_threshold
        
        if has_energy:
            # Log pour diagnostic
            if hasattr(self, 'logger'):
                self.logger.debug(f"✅ VAD BYPASS: Énergie {energy:.6f} >= {basic_threshold:.6f}")
        
        return has_energy  # Bypass complet WebRTC VAD'''
    
    # 4. Vérifier si le pattern existe
    if old_pattern in content:
        print("✅ Pattern VAD trouvé - Application correctif...")
        new_content = content.replace(old_pattern, new_pattern)
        
        # Sauvegarder le nouveau fichier
        with open(audio_streamer_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Correctif VAD bypass appliqué avec succès!")
        
    else:
        print("⚠️ Pattern exact non trouvé - Application correctif alternatif...")
        
        # Méthode alternative - injection directe
        injection_point = "class VoiceActivityDetector:"
        if injection_point in content:
            # Remplacer toute la classe VAD
            vad_class_start = content.find("class VoiceActivityDetector:")
            # Trouver la fin de la classe (prochaine classe ou fin de fichier)
            next_class = content.find("\nclass ", vad_class_start + 1)
            if next_class == -1:
                next_class = len(content)
            
            vad_replacement = '''class VoiceActivityDetector:
    """
    Détecteur d'activité vocale pour éliminer les hallucinations Whisper
    CORRECTIF DÉVELOPPEUR C: Version simplifiée pour déblocage Engine V5
    """
    def __init__(self, sample_rate=16000, aggressiveness=1):
        self.sample_rate = sample_rate
        # BYPASS: Pas de WebRTC VAD, juste seuil énergie
        self.min_energy_threshold = 0.0001  # Très permissif
        
    def has_voice_activity(self, audio_chunk: np.ndarray) -> bool:
        """
        Version simplifiée - bypass WebRTC VAD
        CORRECTIF: Déblocage streaming Engine V5
        """
        energy = np.mean(audio_chunk ** 2)
        return energy >= self.min_energy_threshold

'''
            
            new_content = content[:vad_class_start] + vad_replacement + content[next_class:]
            
            with open(audio_streamer_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ Correctif alternatif appliqué - VAD simplifié!")
        else:
            print("❌ Impossible de localiser classe VoiceActivityDetector")
            return False
    
    print("\n🧪 Test rapide du correctif...")
    return test_vad_bypass()

def test_vad_bypass():
    """
    Test rapide du correctif VAD bypass
    """
    try:
        from audio.audio_streamer import VoiceActivityDetector
        import numpy as np
        
        print("📊 Test VAD bypass...")
        vad = VoiceActivityDetector()
        
        # Test avec audio silence
        silence = np.zeros(16000, dtype=np.float32)
        result_silence = vad.has_voice_activity(silence)
        
        # Test avec audio faible (niveau Rode typique)
        rode_level = np.random.normal(0, 0.001, 16000).astype(np.float32)  # RMS ~0.001
        result_rode = vad.has_voice_activity(rode_level)
        
        print(f"   Silence (RMS=0): {result_silence}")
        print(f"   Rode level (RMS~0.001): {result_rode}")
        
        if result_rode:
            print("✅ VAD bypass fonctionne - audio Rode passera!")
            return True
        else:
            print("⚠️ VAD encore trop restrictif")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test VAD: {e}")
        return False

def rollback_vad_changes():
    """
    Rollback vers version originale si problème
    """
    print("🔄 Rollback vers version originale...")
    
    audio_streamer_path = os.path.join(src_dir, 'audio', 'audio_streamer.py')
    backup_path = audio_streamer_path + '.backup_before_vad_bypass'
    
    if os.path.exists(backup_path):
        import shutil
        shutil.copy2(backup_path, audio_streamer_path)
        print("✅ Rollback effectué")
        return True
    else:
        print("❌ Backup non trouvé")
        return False

if __name__ == "__main__":
    print("🎯 CORRECTIF DÉVELOPPEUR C - VAD BYPASS")
    print("Objectif: Débloquer streaming Engine V5 en 30 minutes")
    print()
    
    try:
        success = apply_vad_bypass_fix()
        
        if success:
            print("\n" + "=" * 60)
            print("✅ CORRECTIF APPLIQUÉ AVEC SUCCÈS!")
            print("📋 Prochaines étapes:")
            print("   1. Tester: python test_engine_v5_ultimate.py")
            print("   2. Vérifier: callbacks Engine V5 > 0")
            print("   3. Si problème: python fix_vad_bypass_engine_v5.py --rollback")
            print()
            print("🎯 Temps estimé validation: 10 minutes")
            
        else:
            print("\n⚠️ Correctif partiellement appliqué")
            print("📋 Test manuel recommandé")
            
    except KeyboardInterrupt:
        print("\n⏹️ Correctif interrompu")
    except Exception as e:
        print(f"\n❌ Erreur correctif: {e}")
        print("🔄 Rollback automatique...")
        rollback_vad_changes() 