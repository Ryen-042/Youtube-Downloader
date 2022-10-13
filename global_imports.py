"""
This module includes all the common imports and variable used in other modules.
"""

import os
from rich.console import Console
from rich.theme import Theme
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Downloads"), exist_ok=True)
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Downloads"))

## Color Scheme:
    # Normal  Text: [normal1] --- [normal2] <var> [/] --- [/]
    # Warning Text: [warning1] ([warning2] <var> [/]) --- [/]
    # File  Exists: [exists] [normal2] <var> [/] --- [/

console = Console(theme=Theme({ "normal1"  :   "bold blue1",
                                "normal2"  :   "bold dark_violet",
                                "warning1" :   "bold plum4",
                                "warning2" :   "bold red",
                                "exists"   :   "bold chartreuse3"
                            }))
