// Fonction pour ajouter des joueurs à la partie
async function addPlayers() {
    // Mise à jour de la liste des joueurs qui vont faire la partie
    if(document.getElementById('listPlayers').innerHTML){
       // La liste contient déjà des joueurs
       document.getElementById('listPlayers').textContent = `${document.getElementById('listPlayers').textContent}, ${document.getElementById('player_textarea').value}`;
    }
    else {
       document.getElementById('listPlayers').textContent = `${document.getElementById('player_textarea').value}`;
    }
    document.getElementById('player_textarea').value = 'Renseignez un nom de joueur'
}

// Fonction pour commencer la partie
async function startGame() {
    const response = await fetch('/api/start_game', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name_players: document.getElementById('listPlayers').textContent }) // Données à envoyer
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
    document.getElementById('addplayer').addEventListener('click', addPlayers);
    document.getElementById('startgame').addEventListener('click', startGame);
}

// Initialisation
function init() {
    setupEventListeners();
    setInterval(updateData, 2000);
}

// Démarrage
document.addEventListener('DOMContentLoaded', init);