from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd
    import tabulate


def to_pretty_string(df: "pd.DataFrame") -> str:
    import pandas as pd
    import tabulate

    return tabulate.tabulate(df, headers="keys", tablefmt="fancy_grid")
