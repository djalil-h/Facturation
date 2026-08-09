# Facturation — version 1.0.0

## Version de production

Cette version correspond à la première version validée de l'application de gestion de facturation de la Pharmacie Hamzaoui Hamid.

### Fonctionnalités validées

- Tableau de bord financier moderne et responsive.
- Gestion des fournisseurs.
- Gestion des factures et des avoirs.
- Sélection des pièces et actions de modification/suppression.
- Gestion des règlements et paiements.
- Historique et journal d'activité.
- Gestion des utilisateurs.
- Paramètres de l'application.
- Centre de notifications.
- Import Excel avec aperçu avant import.
- Détection des doublons.
- Conversion fiable des dates Excel vers JJ/MM/AAAA.
- Calcul des avoirs et de la dette nette.
- Identité visuelle Hamzaoui intégrée.
- Redimensionnement de fenêtre et plein écran.

### Protection des données

- Sauvegarde automatique de la base au démarrage.
- Sauvegarde automatique avant chaque import Excel.
- Sauvegarde SQLite cohérente avec l'API `sqlite3.backup()`.
- Conservation automatique des 30 sauvegardes les plus récentes.
- Une sauvegarde de sécurité est créée avant toute restauration.
- Les sauvegardes, exports, logs et fichiers temporaires ne sont pas versionnés dans Git.

### Base de données

`database/facturation.db` reste la base active de l'application et n'est pas supprimée ni remplacée par cette mise à niveau.
