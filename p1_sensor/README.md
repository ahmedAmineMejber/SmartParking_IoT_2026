# Personne 1 – Capteurs de présence (Simulation)

Ce module implémente la simulation des capteurs de présence du projet
**Smart Parking IoT 2026**.

Chaque capteur simule un capteur de type ultrason mesurant une distance,
détermine automatiquement si une place est **FREE** ou **OCCUPIED**,
et publie l’état via **MQTT** uniquement lorsqu’un changement est détecté.

---

##  Rôle du module

- Simuler des capteurs de présence pour 20 places de parking
- Appliquer une logique réaliste :
  - mesure de distance
  - seuil de détection
  - mécanisme de stabilisation (debounce)
- Publier les états des places via MQTT

Ce module constitue la **source de vérité** pour l’occupation des places.

---

##  Places simulées

Nombre de places : **20**

Identifiants :
P01, P02, P03, … , P20


Chaque place fonctionne de manière indépendante.

---

## Logique de détection

- Une distance est simulée pour chaque place :
  - Place libre : 150–280 cm
  - Place occupée : 10–35 cm
- Un bruit léger est ajouté pour simuler un capteur réel.

### Seuil
THRESHOLD = 50 cm


- distance < 50 cm → OCCUPIED
- distance ≥ 50 cm → FREE

---

##  Debounce (anti-clignotement)

Pour éviter les changements erratiques dus au bruit :
- un changement d’état est validé uniquement après  
  **4 lectures consécutives identiques** (`DEBOUNCE_N = 4`)
- la logique de debounce est interne au capteur

---

## Communication MQTT

### Connexion au broker
- Broker : `broker.emqx.io`
- Port : `1883`
- ClientID : `SmartPark2026_P1`
- Préfixe obligatoire des topics :
smart_parking_2026/


---

### Topic publié

smart_parking_2026/parking/spots/{id}/status


Exemple :
smart_parking_2026/parking/spots/P06/status


---

### Format du message publié (JSON)

```json
{
  "id": "P06",
  "status": "OCCUPIED",
  "distance_cm": 19.8,
  "threshold_cm": 50.0,
  "debounce_n": 4,
  "ts": "2026-01-25T01:23:47"
}

Le message est publié :

    uniquement lors d’un changement d’état

avec l’option retain = true

▶️ Exécution
  Installation des dépendances
      ### pip install paho-mqtt
  Lancement du capteur
      ### python p1_sensor/sensor_p1.py 

▶️ Test A -- Locally :
  1 - Start mosquitto locally:
      mosquitto -v
  2 - In the code, temporarily set:
      BROKER_HOST = "127.0.0.1"
  3 - In another terminal, subscribe:
      mosquitto_sub -h 127.0.0.1 -t "smart_parking_2026/parking/spots/+/status" -v
  4- Run the script:
      python p1_sensor/sensor_p1.py 

▶️ Test B — Integration test with the real broker
  1 - Keep broker as:
      BROKER_HOST = "broker.emqx.io"
      BROKER_PORT = 1883
  2 - Subscribe to the public broker:
      mosquitto_sub -h broker.emqx.io -p 1883 -t "smart_parking_2026/parking/spots/+/status" -v
  3 - Run the script.
      python p1_sensor/sensor_p1.py 