from enum import Enum

#token = "1058570779:AAHtRKeaOOwHUM07shygcc8m8gL6Gzx7H3k" #test bot
#token = "1842814629:AAEJBuXLNi0srZJF2p0AAA4fV4IYNz2e2LM"
token = "1724047584:AAF_dzIhhjfKdX1KPkgQL_PPNmh60HZPA3E"
DBNAME = "pyth_m6"
db_file = "database.vdb"


class States(Enum):
    """
    Мы используем БД Vedis, в которой хранимые значения всегда строки,
    поэтому и тут будем использовать тоже строки (str)
    """
    S_CHAT = "0"  # Начало чата
    S_INACTIVE = "1" # Не в чате
