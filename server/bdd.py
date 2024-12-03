import sqlite3

# Connexion à la base de données
conn = sqlite3.connect('darts.db')
cur = conn.cursor()

# Réinitialisation de la base de données (suppression de la table existante si elle existe)
cur.execute('DROP TABLE IF EXISTS scores')

# Création de la table 'scores' avec un champ 'nom'
cur.execute('''
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    score INTEGER,
    nom TEXT
)
''')

# Insertion de scores avec un nom
cur.execute('INSERT INTO scores (score, nom) VALUES (?, ?)', (100, 'Player 1'))
cur.execute('INSERT INTO scores (score, nom) VALUES (?, ?)', (200, 'Player 2'))

# Récupération et affichage des scores
cur.execute('SELECT * FROM scores')
rows = cur.fetchall()
for row in rows:
    print(row)

# Mise à jour du score
cur.execute('UPDATE scores SET score = ? WHERE id = ?', (800, 1))

# Récupération et affichage des scores après mise à jour
cur.execute('SELECT * FROM scores')
rows = cur.fetchall()
for row in rows:
    print(row)

# Fermeture de la connexion
conn.commit()
conn.close()

