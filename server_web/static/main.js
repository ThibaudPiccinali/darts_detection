// Fonction pour mettre à jour les données
async function updateData() {
    const response = await fetch('/api/data', { method: 'POST' });
    if (response.ok) {
        const data = await response.json();

        // Mise à jour de la table des joueurs et scores
        const playersTable = document.getElementById('playersTable');
        playersTable.innerHTML = '';
        data.players.forEach((player, index) => {
            const row = document.createElement('tr');
            
            // Nom du joueur et parties jouées
            const nameCell = document.createElement('td');
            nameCell.textContent = player;
            
            // Score total
            const scoreCell = document.createElement('td');
            scoreCell.textContent = data.scores[index];
            
            // Détail des scores
            const detailedScoresCell = document.createElement('td');
            if (data.detailed_scores[index].length > 0) {
                detailedScoresCell.textContent = data.detailed_scores[index].join(', ');
            } else {
                detailedScoresCell.textContent = 'Aucun score';
            }

            // Ajouter les cellules à la ligne
            row.appendChild(nameCell);
            row.appendChild(scoreCell);
            row.appendChild(detailedScoresCell);

            // Ajouter la ligne à la table
            playersTable.appendChild(row);
            
        });

        // Mise à jour de la table des dernières flechettes
        const dartsTable = document.getElementById('3dartsTable');
        dartsTable.innerHTML = '';
        const row = document.createElement('tr');
        data.last_darts_score.forEach((dart_score, index) => {
            
            // Détail des scores
            const dartScoreCell = document.createElement('td');
            if (dart_score >= 0) {
                dartScoreCell.textContent = dart_score;
            } else {
                dartScoreCell.textContent = 'Aucun score';
            }
            row.appendChild(dartScoreCell);


        });
        // Ajouter la ligne à la table
        dartsTable.appendChild(row);

        // Mise à jour du joueur actuel et du nombre de joueurs
        document.getElementById('currentPlayer').textContent = `Joueur actuel : ${data.players[data.index_current_player]}`;
        document.getElementById('nbPlayers').textContent = `Nombre de joueurs : ${data.nb_player}`;

        // Mise à jour de l'image de cible
        const dartboardImage = document.getElementById("dartboardImage");
        const timestamp = new Date().getTime(); // Timestamp unique
        dartboardImage.src = `/images/dartboard.png?ts=${timestamp}`;

}
}

// Fonction pour recommencer la partie
async function restartGame() {
    const response = await fetch('/api/restart_game', { method: 'POST' });
    const data = await response.json();
    if (response.ok) {
        alert(data.message);
    } else {
        alert('Erreur lors du reset de la partie.');
    }
}

// Fonction pour terminer la partie
async function endGame() {
    const response = await fetch('/api/end_game', { method: 'POST' });
    const data = await response.json();
    
    if (response.ok) {
        window.location.href = data.redirect_url;
        alert(data.message);
    } else {
        alert('Erreur lors de la fin de la partie.');
    }
}


// Fonction pour changer le score de la fléchette 1
async function change_score_d1() {
    const response = await fetch('/api/change_score_dart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dart_number: "1", new_value: document.getElementById('score_dart1').value}) // Données à envoyer
    }) 
    const data = await response.json();
    if (response.ok) {
        if (data.redirect_url) {
            window.location.href = data.redirect_url;
        }
    } else {
        alert(data.message);
    }
}

// Fonction pour changer le score de la fléchette 2
async function change_score_d2() {
    const response = await fetch('/api/change_score_dart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dart_number: "2", new_value: document.getElementById('score_dart2').value}) // Données à envoyer
    }) 
    const data = await response.json();
    if (response.ok) {
        if (data.redirect_url) {
            window.location.href = data.redirect_url;
        }
    } else {
        alert(data.message);
    }
}

// Fonction pour changer le score de la fléchette 3
async function change_score_d3() {
    const response = await fetch('/api/change_score_dart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dart_number: "3", new_value: document.getElementById('score_dart3').value}) // Données à envoyer
    }) 
    const data = await response.json();
    if (response.ok) {
        if (data.redirect_url) {
            window.location.href = data.redirect_url;
        }
    } else {
        alert(data.message);
    }
}

// Configuration des événements
function setupEventListeners() {
    document.getElementById('restartGame').addEventListener('click', restartGame);
    document.getElementById('endGame').addEventListener('click', endGame);
    document.getElementById('new_score_d1').addEventListener('click', change_score_d1);
    document.getElementById('new_score_d2').addEventListener('click', change_score_d2);
    document.getElementById('new_score_d3').addEventListener('click', change_score_d3);
}

// Initialisation
function init() {
    setupEventListeners();
    setInterval(updateData, 2000);
}

// Démarrage
document.addEventListener('DOMContentLoaded', init);