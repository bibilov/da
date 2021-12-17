import math
import pandas as pd


def highest_five(data, to_search, to_return, searched_str):
    return data[data[to_search].str.lower().str.contains(
        searched_str)][to_return].str.lower().value_counts().head(5)


def main():
    data = pd.read_csv("works.csv").dropna()

    not_same_count = 0
    for (i, j) in zip(data['jobTitle'], data['qualification']):
        if i.lower().replace('-', ' ') != j.lower().replace('-', ' '):
             not_same_count += 1

    print(not_same_count)
    print(highest_five(data, "jobTitle", "qualification", "менеджер"))
    print(highest_five(data, "qualification", "jobTitle", "инженер"))


if __name__ == "__main__":
    main()


# Количество людей,у которых профессия и должность не совпадают (без NaN): 1051
# Топ-5 образований, с которым люди становятся менеджарами:
# бакалавр              11
# менеджер              10
# специалист             6
# экономист              6
# экономист-менеджер     4
# Топ-5 должностей, в которых люди по образованию инженеры:
# заместитель директора          3
# главный инженер                3
# ведущий инженер-конструктор    2
# инженер лесопользования        2
# директор                       2
