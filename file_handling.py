import os


def leaderboard_read(path):
    number = 0
    board = list()
    with open(path, 'r') as leaders:
        for line in leaders:
            try:
                if not line[(line.index(":") + 1):].strip("\n").isdigit():
                    leaders.close()
                    return list(["Error code 1"])
            except ValueError or IndexError:
                return list(["Error code 2"])
            number += 1
            board.append(str(number) + "  " + line[:line.index(":")] + "  " + line[(line.index(":") + 1):].strip("\n"))
        leaders.close()
        return board


def leaderboard_add(path, name, score):
    text_dict = {}
    text = []
    with open(path, 'r') as leaders:
        for line in leaders:
            text.append(line.strip("\n"))
            text_dict.update({str(line.strip("\n")): int(line[(line.index(":") + 1):].strip("\n"))})
        text.append(name + ":" + str(score))
        text_dict.update({str(name + ":" + str(score)): int(score)})
        text = sorted(text, key=text_dict.__getitem__, reverse=True)
        leaders.close()

    with open(path, 'w') as leaders:
        for line_num in range(len(text)):
            if line_num != len(text) - 1:
                leaders.write(text[line_num] + "\n")
            else:
                leaders.write(text[line_num])
        leaders.close()
        return

#print(leaderboard_add("resources/leaderboard/leaderboard.txt", "sdf0", "123"))