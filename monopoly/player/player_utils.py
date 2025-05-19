from settings import GameMechanics


def net_worth(money, owned, count_mortgaged_as_full_value=False):
    """ Calculate player's net worth (cache + property + houses)
    count_mortgaged_as_full_value determines if we consider property mortgaged status:
    - True: count as full, for Income Tax calculation
    - False: count partially, for net worth statistics
    """
    net_worth = int(money)
    
    for cell in owned:
        
        if cell.is_mortgaged and not count_mortgaged_as_full_value:
            # Partially count mortgaged properties
            net_worth += int(cell.cost_base * (1 - GameMechanics.mortgage_value))
        else:
            net_worth += cell.cost_base
            net_worth += (cell.has_houses + cell.has_hotel) * cell.cost_house
    
    return net_worth