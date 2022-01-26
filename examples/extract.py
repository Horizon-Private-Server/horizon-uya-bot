
lines = []
with open('all.txt', 'r') as f:
    for line in f:
        line = line.strip()
        if "dmetcp" in line:
            protocol = 'TCP'
            if '34465' in line and ' I ' in line:
                player = 'P0'
            elif '46719' in line and ' I ' in line:
                player = 'P1'
        else:
            protocol = 'UDP'
            if '57069' in line and ' I ' in line:
                player = 'P0'
            elif '52976' in line and ' I ' in line:
                player = 'P1'
        print(f"{protocol} {player} {line.split(' | ')[-1]}")

           
