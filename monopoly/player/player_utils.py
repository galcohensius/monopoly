from settings import GameMechanics


def net_worth(money, owned, count_mortgaged_as_full_value=False):
    """ Calculate player's net worth (cash + property + houses)
    `count_mortgaged_as_full_value` determines if we consider property mortgaged status:
    - True: count as full, for Income Tax calculation
    - False: count partially, for net worth statistics
    """
    net_value = int(money)
    
    for cell in owned:
        if cell.is_mortgaged and not count_mortgaged_as_full_value:
            net_value += int(cell.cost_base * (1 - GameMechanics.mortgage_value))
        else:
            net_value += cell.cost_base
            net_value += (cell.has_houses + cell.has_hotel) * cell.cost_house

    return net_value


def get_ordinal_str(house_number: int) -> str:
    """Return '1st', '2nd', … for 1-4; otherwise '<n>th'."""
    ordinal = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th"}
    return ordinal.get(house_number, f"{house_number}th")