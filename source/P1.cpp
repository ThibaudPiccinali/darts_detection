#include "object.h"

int main() {

    std::vector<Player> players = {Player(1, "Thibaud"), Player(2, "Bob")};
    Game game(players, 301);
    printf("%s\n",game.to_json().dump().c_str());

    return 0;
}