def get_link():
    new_link = input("Enter link: ")
    while not new_link.strip():
        new_link = input("Nothing entered. Please enter a valid link: ")
    return new_link.strip()
