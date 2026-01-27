# Smart Parking IoT 2026 - Infrastructure MQTT

[cite_start]Ce dépôt contient l'infrastructure de communication pour le projet de parking intelligent[cite: 14]. [cite_start]En tant que responsable de la communication (Personne 5), j'ai mis en place ce cadre pour assurer une interopérabilité totale entre nos différents modules[cite: 1, 10].

##  Informations de Connexion au Broker
Tous les modules doivent utiliser les paramètres suivants pour se connecter au réseau :
* [cite_start]**Adresse du Broker :** `broker.emqx.io` [cite: 2, 14]
* [cite_start]**Port :** `1883` [cite: 3, 14]
* [cite_start]**Préfixe obligatoire pour chaque topic :** `smart_parking_2026/` [cite: 4, 15]

##  Vos Identifiants (ClientID)
[cite_start]Pour éviter les déconnexions en boucle, chaque membre de l'équipe **doit** utiliser son ClientID spécifique dans son code[cite: 5, 14]:
* [cite_start]**Personne 1 (Capteurs) :** `SmartPark2026_P1` [cite: 6, 14]
* [cite_start]**Personne 2 (Logique) :** `SmartPark2026_P2` [cite: 7, 14]
* [cite_start]**Personne 3 (Barrière) :** `SmartPark2026_P3` [cite: 8, 14]
* [cite_start]**Personne 4 (Afficheur) :** `SmartPark2026_P4` [cite: 9, 14]
* [cite_start]**Personne 5 (Com & Monitoring) :** `SmartPark2026_P5` [cite: 10, 14]
* [cite_start]**Personne 6 (Backend & API) :** `SmartPark2026_P6` [cite: 11, 14]
* [cite_start]**Personne 7 (Dashboard IoT) :** `SmartPark2026_P7` [cite: 12, 14]

##  Table des Topics et Formats JSON
Voici la "partition" que chaque module doit suivre. [cite_start]Les `...` dans les topics doivent être remplacés par le préfixe `smart_parking_2026/`[cite: 14, 15].

| Responsable | Action | Topic MQTT | Format du Message (JSON) |
| :--- | :--- | :--- | :--- |
| **P1** | Publie | `.../parking/spots/{id}/status` | [cite_start]`{"id": "A1", "status": "FREE"}` [cite: 14] |
| **P2** | S'abonne | `.../parking/spots/+/status` | [cite_start]*(Détection d'arrivée de véhicule)* [cite: 14] |
| **P2** | S'abonne | `.../parking/display/available` | [cite_start]*(Vérification des places libres)* [cite: 14] |
| **P2** | Publie | `.../parking/barriers/entry/cmd` | [cite_start]`{"action": "OPEN"}` [cite: 14] |
| **P3** | S'abonne | `.../parking/barriers/entry/cmd` | [cite_start]*(Attente d'ordre d'ouverture)* [cite: 14] |
| **P3** | Publie | `.../parking/barriers/entry/state` | [cite_start]`{"state": "OPENED"}` [cite: 14] |
| **P4** | S'abonne | `.../parking/spots/+/status` | [cite_start]*(Écoute P1 pour calcul interne)* [cite: 14] |
| **P4** | Publie | `.../parking/display/available` | [cite_start]`{"count": 12}` [cite: 14] |
| **P6** | S'abonne | `.../parking/#` | [cite_start]*(Historisation globale)* [cite: 14] |
| **P6** | Publie | `.../parking/config/new_spot` | [cite_start]`{"id": "B1", "cmd": "ADD"}` [cite: 14] |
| **P7** | S'abonne | `.../parking/#` | [cite_start]*(Visualisation en temps réel)* [cite: 14] |
| **P7** | Publie | `.../parking/admin/override` | [cite_start]`{"cmd": "FORCE_OPEN"}` [cite: 14] |

##  Instructions pour l'équipe
1.  Téléchargez le fichier `client_template.py`.
2.  Changez la variable `CLIENT_ID` à la ligne 9 avec l'identifiant qui vous a été attribué ci-dessus.
3.  Adaptez la section `ABONNEMENTS` et la `LOGIQUE D'ENVOI` selon votre rôle dans la table.
4.  Utilisez toujours `json.dumps()` pour vos publications afin de garantir un format JSON valide.
