import sqlite3

# Connect to the database and get the cursor
con = sqlite3.connect("replikant.db")
con.row_factory = sqlite3.Row
cur = con.cursor()

update_content = []
for table_name in ["Task_training", "Task_core"]:
    res = cur.execute(f"select * from {table_name} where info_type not like 'rank_score_%'");
    info_types = set()
    for cur_row in res:
        row_id = cur_row['id']
        info_type = cur_row['info_type']
        step_idx = cur_row['step_idx'] + 1
        info_types.add(info_type)

        update_content.append(f"update {table_name} set step_idx={step_idx} where id = '{row_id}'")

    print(info_types)


# Now execute the cleaning
script = "BEGIN;\n"
script +=  ';\n'.join(update_content) + ";\n"
script += "COMMIT;"
cur.executescript(script)


# Prepare the fix as monitoring steps are plain
cur.close()
con.close()
