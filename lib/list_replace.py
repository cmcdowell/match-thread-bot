def list_replace(lst, changes):
    team_string = '+'.join(lst)
    for change in changes:
        team_string = team_string.replace(change[0], change[1])
    team_string = team_string.lower()
    team_string = team_string.replace(' ', '')

    return team_string.split('+')
