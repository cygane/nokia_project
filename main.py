import ahocorasick
import os

def build_automaton(patterns):
    A = ahocorasick.Automaton()
    for idx, pattern in enumerate(patterns):
        A.add_word(pattern, (idx, pattern))
    A.make_automaton()
    return A

def search_in_file(automaton, file_path):
    results = []
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        for end_idx, (idx, pattern) in automaton.iter(content):
            start_idx = end_idx - len(pattern) + 1
            results.append((idx, start_idx, end_idx))
    
    return results

def search_words_in_directory(directory, patterns):
    automaton = build_automaton(patterns)
    results = {}
    
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            matches = search_in_file(automaton, file_path)
            if matches:
                results[file_path] = matches
    
    return results

if __name__ == "__main__":
    search_directory = "./files"
    words_to_find = ["error", "warning", "critical"]
    
    matches = search_words_in_directory(search_directory, words_to_find)
    for file, occurrences in matches.items():
        print(f"In file: {file}")
        for match in occurrences:
            print(f"  - Found pattern '{words_to_find[match[0]]}' at position {match[1]}-{match[2]}")
