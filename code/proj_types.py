from enum import Enum

# This file defines all the important enum types required for the system
# to function.

# we'll call this in various files where the defintiion of State is important.
# State defines the relationship between the LA and the A; further info
# is available in the models file.
class State(Enum):
    Working = 1
    Pending = 2
    Accepted = 3
    Rejected = 4
