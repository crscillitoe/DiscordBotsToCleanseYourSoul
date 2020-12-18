from constants_two import color_dictionary
for key, val in enumerate(color_dictionary):
    print(f"{{ red: {val[0]}, green: {val[1]}, blue: {val[2]}, imageName: \"{color_dictionary[val]}\" }}, ")