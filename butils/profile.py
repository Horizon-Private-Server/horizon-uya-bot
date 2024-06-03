import pandas as pd
import os
import random
import numpy as np

class Profile:
    def __init__(self, profile_id):
        
        current_directory = os.path.dirname(os.path.abspath(__file__))

        profiles = current_directory + '/../profiles.csv'

        df = pd.read_csv(profiles)
        df = df.replace({np.nan: None})

        result = df[df['profile'] == profile_id]
        result = result.to_dict(orient='records')[0]

        for key, val in result.items():
            self.__dict__[key] = val

        print(self)

        if self.overall_skill > 8:
            self.bolt = 4
        elif self.overall_skill > 5:
            self.bolt = 3
        elif self.overall_skill > 3:
            self.bolt = 2
        else:
            self.bolt = 1

        skins = [skin.strip() for skin in self.skins.split(",") if skin.strip()]
        self.skin = random.choice(skins)

        if self.alts:
            alts = [alt.strip() for alt in self.alts.split(",") if alt.strip()] + [self.username]
        else:
            alts = [self.username]
        self.username = random.choice(alts)
        self.username = self.username[:14]

    def __str__(self):
        result = 'Profile; '
        for attr in dir(self):
            if not attr.startswith('_'):
                val = eval(f"self.{attr}")
                result += f'{attr}:{val} '
        return result.strip()