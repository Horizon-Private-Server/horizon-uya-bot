

if __name__ == '__main__':
    import pandas as pd

    df = pd.read_csv('ctf_bot_states.csv')

    print("if False:")
    print("    pass")
    for _, row in df.iterrows():
        print(f"elif home_flag == '{row['home_flag']}'  and enemy_flag == '{row['enemy_flag']}' and {row['ally']} and {row['enemy']}:")
        print(f"    state = '{row['state']}'")