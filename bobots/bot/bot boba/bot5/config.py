from enum import Enum

#token = "1058570779:AAHtRKeaOOwHUM07shygcc8m8gL6Gzx7H3k" #test bot
#token = "1842814629:AAEJBuXLNi0srZJF2p0AAA4fV4IYNz2e2LM"
token = "1873585029:AAEfEahrg07k4P0UFvk0VDGXtBclPiD2h9U"
DBNAME = "pyth_m5"
db_file = "database.vdb"


class States(Enum):
    """
    Мы используем БД Vedis, в которой хранимые значения всегда строки,
    поэтому и тут будем использовать тоже строки (str)
    """
    S_CHAT = "0"  # Начало чата
    S_INACTIVE = "1" # Не в чате
