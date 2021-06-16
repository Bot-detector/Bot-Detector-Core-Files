import os
import string
import random
import pathlib
import pandas as pd

import SQL
import errors


def create_ban_export(file_type, linked_accounts, display_name, discord_id):

    pathlib.Path(f"{os.getcwd()}/exports/").mkdir(parents=True, exist_ok=True)

    export_data = {}

    export_data["url_text"] = create_random_link()
    export_data["discord_id"] = discord_id

    if file_type == "csv":
        csv_file_name = create_csv_export(
            linked_accounts=linked_accounts,
            display_name=display_name
        )

        export_data["file_name"] = csv_file_name
        export_data["is_csv"] = 1


    elif file_type == "excel":
        excel_file_name = create_excel_export(
            linked_accounts=linked_accounts, 
            display_name=display_name
        )

        export_data["file_name"] = excel_file_name
        export_data["is_excel"] = 1

    else:
        raise errors.InvalidFileType

    SQL.insert_export_link(export_data)

    return export_data.get("url_text")


def create_excel_export(linked_accounts, display_name):
    sheets = []
    names = []

    for account in linked_accounts:
        data = SQL.get_player_banned_bots(account.name)
        df = pd.DataFrame(data)

        sheets.append(df)
        names.append(account.name)

    if len(sheets) > 0:
        totalSheet = pd.concat(sheets)
        totalSheet = totalSheet.drop_duplicates(inplace=False, subset=["Player_id"], keep="last")

        file_name = f"{display_name}_bans.xlsx"
        file_path = f"{os.getcwd()}/exports/" + file_name

        writer = pd.ExcelWriter(file_path, engine="xlsxwriter")

        totalSheet.to_excel(writer, sheet_name="Total")

        for idx, name in enumerate(names):
            sheets[idx].to_excel(writer, sheet_name=names[idx])

        writer.save()

        return file_name

    else:
        raise errors.NoDataAvailable


def create_csv_export(linked_accounts, display_name):
    sheets = []

    for account in linked_accounts:
        data = SQL.get_player_banned_bots(account.name)
        df = pd.DataFrame(data)

        sheets.append(df)

    totalSheet = pd.concat(sheets)
    totalSheet = totalSheet.drop_duplicates(inplace=False, subset=["Player_id"], keep="last")

    file_name = f"{display_name}_bans.csv"
    file_path = f"{os.getcwd()}/exports/" + file_name

    totalSheet.to_csv(file_path, encoding='utf-8', index=False)


def create_random_link():
    pool = string.ascii_letters + string.digits

    link = ''.join(random.choice(pool) for i in range(12))

    return link


def get_export_file_path():
    pass