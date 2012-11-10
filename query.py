#! usr/bin/env python

import sqlite3


def query_fixtures():

    changes = [('West Bromwich Albion', 'westbrom'),
               ('Manchester United', 'manchester-united'),
               ('Tottenham Hotspur', 'tottenham-hotspur'),
               ('Swansea City', 'swansea'),
               ('Queens Park Rangers', 'qpr'),
               ('Aston Villa', 'aston-villa')]

    con = sqlite3.connect('fixtures.db')
    cursor = con.cursor()
                        # DATETIME(kick_off) < DATETIME('now')

    with con:
        cursor.execute("""
                    SELECT * FROM fixtures_tbl LIMIT 3;
                       """)

        rows = cursor.fetchall()
        fixture_list = []

        for row in rows:
            fixture_list.append(list(row))

        away_list, home_list = [], []

        for row in fixture_list:
            away_list.append(row[3])

        for row in fixture_list:
            home_list.append(row[2])

        home_list = list_replace(home_list, changes)
        away_list = list_replace(away_list, changes)

        for i, row in enumerate(fixture_list):
            row.append(home_list[i])
            row.append(away_list[i])

        return fixture_list


def list_replace(lst, changes):
    team_string = '+'.join(lst)
    for change in changes:
        team_string = team_string.replace(change[0], change[1])
    team_string = team_string.lower()
    team_string = team_string.replace(' ', '')

    return team_string.split('+')
