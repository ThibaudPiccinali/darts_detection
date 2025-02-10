#include "object.h"

int main() {

    std::vector<Player> players = {Player(1, "Thibaud"), Player(2, "Bob")};
    Game game(players, 301);
    game.display();
    game.players[game.index_current_player].display();
    return 0;
}