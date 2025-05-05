import random

N_TO_GEN = 30000


prefixes = [
    "Shadow", "Neo", "Dark", "Ultra", "Mega", "Hyper", "Iron", "Silver", "Rapid", "Fire",
    "Storm", "Night", "Steel", "Cyber", "Ghost", "Crimson", "Blaze", "Phantom", "Venom", "Arctic",
    "Frost", "Toxic", "Quantum", "Pulse", "Viper", "Inferno", "Nova", "Oblivion", "Eclipse", "Silent",
    "Swift", "Thunder", "Rogue", "Black", "Crush", "Zero", "Alpha", "Omega", "Echo", "Fallen"
]

modifiers = [
    "", "Dark", "Fast", "Wild", "Epic", "Prime", "Turbo", "Lucky", "Silent", "Fire", "Fury", "Steel",
    "Ghost", "Venom", "Arc", "Volt", "Storm", "Blaze", "Frost", "Vortex"
]

suffixes = [
    "Hunter", "Master", "Slayer", "Knight", "Wolf", "Vortex", "Sniper", "Rider", "Gamer", "X",
    "Nova", "Strike", "Blade", "Crusher", "Predator", "Storm", "Fury", "Raider", "Falcon", "Specter",
    "Dragon", "Phantom", "Titan", "Assassin", "Archer", "Berserker", "Breaker", "Reaper"
]

numbers = [str(n) for n in range(1, 5000)]  # lower number range to avoid over-dependence

single_words = [
    "Shadow", "Crimson", "Blaze", "Nova", "Phantom", "Vortex", "Fury", "Specter", "Nightfall", "Oblivion",
    "Inferno", "Pulse", "Venom", "Arctic", "Silent", "Eclipse", "Storm", "Titan", "Viper", "Quantum",
    "Swift", "Thunder", "Zero", "Alpha", "Omega"
]

usernames = set()

def generate_username():
    if random.random() < 0.05:  # 5% single-word usernames
        return random.choice(single_words)
    else:
        prefix = random.choice(prefixes)
        modifier = random.choice(modifiers)
        suffix = random.choice(suffixes)
        name = f"{prefix}{modifier}{suffix}"
        if random.random() < 0.3:  # only 30% chance to add a number
            name += random.choice(numbers)
        return name

while len(usernames) < N_TO_GEN:
    usernames.add(generate_username())

with open("usernames.txt", "w", encoding="utf-8") as f:
    for name in sorted(usernames):
        f.write(name + "\n")

print("Generated 30,000 unique usernames with minimal overlap.")
