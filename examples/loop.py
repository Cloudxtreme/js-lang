def sum_numbers(N):
    s = 0.0
    i = 0.0
    while i < N:
        s += i
        i += 1.0
    return s


print sum_numbers(30000000)

