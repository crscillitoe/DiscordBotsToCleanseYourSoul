from constants_two import color_dictionary
for key, val in enumerate(color_dictionary):
    print(f"<img id=\"{color_dictionary[val]}\" src=\"/assets/svgs/{color_dictionary[val]}.svg\">")