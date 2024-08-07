import pandas as pd

# import resale dataset

path = "data/cleaned_data/resales_processed_"

resales1 = pd.read_csv(path + "aa")
resales2 = pd.read_csv(path + "ab")
resales3 = pd.read_csv(path + "ac")
resales4 = pd.read_csv(path + "ad")
resales5 = pd.read_csv(path + "ae")
resales6 = pd.read_csv(path + "af")
resales7 = pd.read_csv(path + "ag")
resales8 = pd.read_csv(path + "ah")
resales9 = pd.read_csv(path + "ai")
resales10 = pd.read_csv(path + "aj")

columns = resales1.columns
for df in [resales2, resales3, resales4, resales5, resales6, resales7, resales8, resales9, resales10]:
    df.columns = columns

resales = pd.concat([resales1, resales2, resales3, resales4, resales5, resales6, resales7, resales8, resales9, resales10], axis=0, ignore_index=True)

# import rental dataset

rentals = pd.read_csv("data/cleaned_data/rentals_processed.csv")
