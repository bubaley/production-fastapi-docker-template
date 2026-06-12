def round_half_up(n, digits=0):
    factor = 10**digits
    result = int(n * factor + 0.5) / factor
    return result if result % 1 else int(result)
