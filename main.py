import pandas as pd


def main():
    works = pd.read_csv("works.csv").dropna()  # Импорт библиотеки

    count_not_same = 0
    for (i, j) in zip(works['jobTitle'], works['qualification']):
        if i.lower().replace('-', ' ') != j.lower().replace('-', ' '):
            count_not_same += 1

    print(count_not_same)  # вывод количества не совпадающих профессий и должностей (1051)
    print(
        top_five(works, "qualification", "jobTitle", "инженер"))  # Топ-5 образований, с которым становятся менеджерами
    print(
        top_five(works, "jobTitle", "qualification", "менеджер"))  # Топ-5 образований, с которым становятся инженерами


def top_five(works, to_search, to_return, searched_str):
    return works[works[to_search].str.lower().str.contains(
        searched_str)][to_return].str.lower().value_counts().head(5)


if __name__ == "__main__":
    main()
