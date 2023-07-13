import nltk
nltk.download("punkt")


def map_substring_indices(full_string: str, list_of_substrings: list) -> list:
    """
    Input:
        full_string: "This is a sentence"
        list_of_substrings: ["This", "is", "a", "sentence"]

    Output:
        [[0, 4], [5, 7], [8, 9], [10, 18]]
    """

    start, indices = 0, []

    for substring in list_of_substrings:
        start = full_string.find(substring, start)
        end = start + len(substring)
        indices.append([start, end])
        start = end
    
    return indices


def find_sentences(text: str) -> list:
    """
    Input:
        text: "This is a sentence. This is another sentence."

    Output:
        ["This is a sentence.", "This is another sentence."]
    """

    return nltk.sent_tokenize(text)
