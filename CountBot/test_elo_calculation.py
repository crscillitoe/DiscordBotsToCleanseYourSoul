from bot2 import compute_rating_score

players = [
    ["Christian", 12000, 0],
    ["Katie", 255, 1],
    ["Jeff", 147, 1],
    ["Joel", 108, 0],
    ["Ivan", 145, 3],
    ["Evan", 117, 3],
    ["Zacc", 74, 2],
    ["Jordn", 33, 0],
    ["Ethan", 103, 4],
    ["Lisa", 21, 0],
    ["Zac", 2, 0],
]

for player in players:
    print("{}s ELO: {}".format(player[0], compute_rating_score(player[1], player[2], 0, 0)[0]))
