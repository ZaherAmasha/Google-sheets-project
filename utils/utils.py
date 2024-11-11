def remove_elements_with_whitespaces_and_empty_from_list(_list):
    """Removes elements in a list that are pure whitespaces or empty.
    Needed to filter usable keywords from user input.
    """
    return [element for element in _list if element.strip()]
