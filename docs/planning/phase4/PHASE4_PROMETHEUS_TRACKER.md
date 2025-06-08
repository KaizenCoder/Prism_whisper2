# Phase 4 : Projet Prometheus - Intégration Talon

**Objectif :** Transformer Talon en une simple "coquille d'exécution" dont le SuperWhisper V5 devient la seule et unique source de reconnaissance vocale.

## Feuille de Route Détaillée (Estimé : 16h)

### Jour 1 : Recherche & Connexion (8h)
| ID    | Tâche                    | Statut | Temps | Livrable                                                                             |
|-------|--------------------------|--------|-------|--------------------------------------------------------------------------------------|
| 4.1.1 | Analyse API Talon        | [ ]    | 3h    | Script de "preuve de concept" (`talon_rpc_poc.py`) forçant l'exécution d'une commande. |
| 4.1.2 | Préparation Environnement | [x]    | 2h    | Documentation claire (`PHASE4_ENV.md`) sur la configuration requise.                 |
| 4.1.3 | Architecture Bridge V5   | [ ]    | 3h    | Squelette de la classe `PrismBridgeV5` avec interfaces de connexion/communication.    |

### Jour 2 : Intégration & Validation (8h)
| ID    | Tâche                      | Statut | Temps | Livrable                                                                            |
|-------|----------------------------|--------|-------|-------------------------------------------------------------------------------------|
| 4.2.1 | Développement Bridge V5    | [ ]    | 4h    | Version complète et fonctionnelle du `PrismBridgeV5`.                               |
| 4.2.2 | Intégration Interfaces     | [ ]    | 2h    | Mise à jour du System Tray pour refléter l'état de la connexion à Talon.            |
| 4.2.3 | Validation de Bout en Bout | [ ]    | 2h    | Tests documentés (`PHASE4_E2E.md`) validant des commandes simples et complexes.      | 