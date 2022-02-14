
import pandas as pd

def _add_A17(df):

    df2 = df
    df2["A17"] = df2["A38"]
    df2["A17"] = df2["A17"].replace(to_replace ='^B|^D|^E', value = 'DE', regex = True)
    df2["A17"] = df2["A17"].replace(to_replace ='^A!', value = 'AZ', regex = True)

    string = "|".join(["^" + s + "!" for s in ["B", "D", "E"]])
    df2["A17"] = df2["A17"].replace(to_replace = string, value = 'DE', regex = True)

    string = "|".join(["^" + s + "!" for s in ["CA"]])
    df2["A17"] = df2["A17"].replace(to_replace = string, value = 'C1', regex = True)

    string = "|".join(["^" + s + "!" for s in ["CD"]])
    df2["A17"] = df2["A17"].replace(to_replace = string, value = 'C2', regex = True)    

    string = "|".join(["^" + s + "!" for s in ["CI", "CJ", "CK"]])
    df2["A17"] = df2["A17"].replace(to_replace = string, value = 'C3', regex = True)

    string = "|".join(["^" + s + "!" for s in ["CL"]])
    df2["A17"] = df2["A17"].replace(to_replace = string, value = 'C4', regex = True)

    string = "|".join(["^" + s + "!" for s in ["CB", "CC", "CE", "CF", "CG", "CH", "CM"]])
    df2["A17"] = df2["A17"].replace(to_replace = string, value = 'C5', regex = True)

    df2["A17"] = df2["A17"].replace(to_replace ='^J', value = 'JZ', regex = True)

    df2["A17"] = df2["A17"].replace(to_replace ='^M|^N', value = 'MN', regex = True)

    df2["A17"] = df2["A17"].replace(to_replace ='^O|^P|^Q', value = 'OQ', regex = True)

    df2["A17"] = df2["A17"].replace(to_replace ='^R|^S|^T|^U', value = 'RU', regex = True)

    def _move_col_after(df, col, col_ref):
            if col in df.columns:
                if col_ref in df.columns:
                    loc_var = df.columns.get_loc(col_ref)
                    col2insert = df[col]
                    df = df.drop([col], axis=1)
                    df.insert(loc_var + 1, col, col2insert)
            return(df)

    df2 = _move_col_after(df2, "A17", "A10")

    return df2
    