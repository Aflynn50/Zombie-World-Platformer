import os


def leaderboard_read(path):
    number = 0
    board = list()
    try:
        with open(path, 'r') as leaders:  # The with statement means that the file will close automatically when it is closed
            for line in leaders:
                try:
                    if not line[(line.index(":") + 1):].strip("\n").isdigit():  # Check if the file is in the correct format
                        leaders.close()
                        return list(["The file is in the incorrect format (Error Code 1)"])
                except ValueError or IndexError:
                    return list(["The file is in the incorrect format (Error Code 2)"])  # The error code will tell any tester which error has been found with the file
                number += 1
                board.append(str(number) + "  " + line[:line.index(":")] + "  " + line[(line.index(":") + 1):].strip("\n"))  # Appends the string for each line to be displayed on the leaderboard screen
            leaders.close()  # Close the leaderboard
            return board
    except FileNotFoundError:
        print("File missing")
        return list()


def leaderboard_check(path):  # Function to check the scores of the entries in the leaderboard file
    board = list()
    try:
        with open(path, 'r') as leaders:
            try:
                for line in leaders:
                    board.append(int(line[(line.index(":") + 1):].strip("\n")))  # Adds each score into the list
            except ValueError or IndexError:
                print("The file is in the incorrect format")
            leaders.close()
            return board
    except FileNotFoundError:
        print("File missing")
        return list()


def leaderboard_add(path, name, score):
    dict_text = {}  # Initialises a dictionary
    text = []
    try:
        with open(path, 'r') as leaders:
            try:
                for line in leaders:
                    text.append(line.strip("\n"))  # Add each line onto the text variable but strip off the new line character on the end
                    dict_text.update({str(line.strip("\n")): int(line[(line.index(":") + 1):].strip("\n"))})  # Adds each line to the dictionary with it corresponding score as a integer variable type
            except ValueError or IndexError:
                print("The file is in the incorrect format")
            leaders.close()
    except FileNotFoundError:  # If the file doesnt exist then a new file is created so no error is thrown
        pass

    text.append(name + ":" + str(
        score))  # Add the new name and score of the player who has just completed the level to the text list
    dict_text.update({text[-1]: int(score)})  # Adds the new line to the dictionary along with the score
    text = sorted(text, key=dict_text.__getitem__, reverse=True)  # Sorts the items in the text file according to the scores of each player

    with open(path, 'w') as leaders:  # Creates new file for writing to
        for line_num in range(len(text)):
            if line_num != len(text) - 1:
                leaders.write(text[line_num] + "\n")  # Write the newly sorted text list back into the now empty leader board text file
            else:
                leaders.write(text[line_num])
        leaders.close()
        return


def key_bindings_read(path, default_bindings):
    try:
        with open(path, 'r') as key_bindings:  # Opens the key bindings file for reading
            try:
                for line in key_bindings:
                    if str(line[:line.index(":")]) in default_bindings:  # Checks if the key is one that can be assigned
                        default_bindings[(str(line[:line.index(":")]))] = int(line[(line.index(":") + 1):].strip("\n"))  # Sets the entry for that key in the key dictionary to the key in the file
            except ValueError or IndexError:
                print("The file is in the incorrect format")
            key_bindings.close()
            return default_bindings
    except FileNotFoundError:
        print("File missing")
        return default_bindings


def settings_read(path):
    try:
        dict_settings = dict()
        with open(path, 'r') as settings:
            for line in settings:
                try:
                    dict_settings[str(line[:line.index(":")])] = line[(line.index(":") + 1):].strip("\n")  # Changes the settings to what is written in the settings file
                except ValueError or IndexError:
                    print("The file is in the incorrect format")
            settings.close()
            return dict_settings
    except FileNotFoundError:
        print("File missing")
        return dict_settings


def settings_update(path, dict_settings):
    list_dict = list(dict_settings.items())
    with open(path, 'w') as settings:
        for entry_num in range(len(list_dict)):
            if entry_num != len(list_dict) - 1:  # Checks if it is the last line in the file
                settings.write(list_dict[entry_num][0] + ":" + list_dict[entry_num][1] + "\n")  # Writes the name of the setting and its state to the settings file
            else:
                settings.write(list_dict[entry_num][0] + ":" + list_dict[entry_num][1])
        settings.close()


def load_maps(path):  # Gets a list of all the maps in the maps folder
    path_list = list()
    for level in os.listdir(path):   # Cycles through the files in the folder
        if level.endswith(".tmx"):  # Checks if it is a map file
            path_list.append(level)
    return path_list
