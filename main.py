total_g_in = 4380237

inputs = {
    'gold_total': total_g_in,
    'gold_coffer': 72000,
    'ore_in': 2700,
    'coal_in': 8100,
    'potion_in': 9,
}


g_available = int(input())

for i in range(9,0, -1):
    if total_g_in // (i/9) < g_available:
        break


print(f'fraction: {i}')
for name, quantity in inputs.items():
    print(f'{name}: {quantity*(i/9)}')
