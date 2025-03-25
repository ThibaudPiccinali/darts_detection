# Dart'O'Matic :dart:
**Thibaud PICCINALI**

Ce dépôt présente l'ensemble des codes que j'ai pu développer dans le cadre de mon projet d'intégration (PDI) au sein de l'Ecole Centrale de Lille. Ce projet consiste en un système de gestion automatique de parties de fléchettes. Il comporte notamment des modules de détection de position de fléchette.

## Setup

Ce système a été conçu avec l'utilisation de deux caméras. Pour pouvoir utiliser ces dernières et réaliser l'estimation de position, leurs paramètres intrinsèques doivent être connus.

Le script ```setup.py```  vous aidera à trouver ces paramètres. Ce script a été réalisé à l'aide de l'excellent dépôt de M.Temuge Batpurev que je vous recommande d'aller étudier pour mieux comprendre cette étape de calibration : https://github.com/TemugeB/python_stereo_camera_calibrate. Vous aurez notamment besoin de prendre un certain nombre de photo d'échiquier et de les disposer dans les dossiers ```setup_images/calibration``` et ```setup_images/synch``` correspondant. Des images d'exemple sont présentées dans ce dépôt pour une meilleure compréhension des résultats attendus. 

Ce script se déroule ensuite en trois étapes :

- D'abord l'estimation des matrices intrinsèques des caméras
- Puis l'estimation des positions relatives des caméras
- Enfin, la détermination de l'origine du repère de la cible. Vous devrez pour se faire cliquer sur le centre de la cible sur les images prise par vos caméras qui vont apparaître, en appuyant sur la touche `q` pour valider.


Une fois ce script exécuté, le fichier de configuration ```config.yaml``` devrait correctement être édité.

## Fonctionnement

Pour lancer le système, il suffit de lancer l'exécutable ```bin\main```.

Prenez garde aux points suivants : 

- Que les caméras soient bien connectées
- Qu'elles soient bien configurées sur le bon port (vous pouvez modifier ces ports dans le fichier ```source/main.cpp```)
- Que la haut de la cible soit orientée vers la caméra 1 (celle qui sert de référence pour la calibration)

Une fois lancé, le système devrait être prêt à commencer une partie.

## Serveur web

Le pilotage de la partie s'effectue à l'aide d'une interface web. Il suffit de la lancer à l'aide du script ```server_web/app.py``` et de se rendre sur le lien http://127.0.0.1:5000. Vous pourrez ainsi gérer l'ensemble de la partie via ce site web.

A noter que l'adresse réseau de la machine où s'exécute le code principal doit être configurée dans le fichier ```server_web/app.py``` au sein de la fonction ```send_command```.

## Démonstration

Pour une démonstration du système, vous pouvez visionner la vidéo suivante :
https://youtu.be/i5ayhuvZMgI?si=fUC4OQUIXnoK02U6
