PAIR_WEIGHT = 2


def count_entries2(words, text):
    count = 0
    words = words.split(' ')
    for i in range(len(words)-1):
        if words[i] in text:
            count += 1
            pair = ' '.join((words[i], words[i+1]))
            if pair in text:
                count += PAIR_WEIGHT
    if words[-1] in text:
        count += 1
    return count
