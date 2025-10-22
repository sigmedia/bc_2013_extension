import shutil
import pathlib
import sqlite3


###########################################################################################
## Initialisation
###########################################################################################

DEBUG=False

# Copy the file
shutil.copy(pathlib.Path("flexeval.db"), pathlib.Path("replikant.db"))

# Initialise the database connection and cursor
con = sqlite3.connect("replikant.db")
con.row_factory = sqlite3.Row
cur = con.cursor()

def execute(script):
    print(script)
    if not DEBUG:
        cur.executescript(script)

###########################################################################################
## Rename the tables
###########################################################################################

# Rename the non-dynamically created tables
script = "BEGIN;\n"
script += "ALTER TABLE StageModuleUser RENAME TO Participants;\n"
# script += "ALTER TABLE AdminModuleUser RENAME TO Administrators;\n"
script += "COMMIT;"
execute(script)

# Rename test tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t["name"] for t in cur.fetchall()]
tables = list(filter(lambda x: x not in ["Participants", "Sample", "Administrators", "sqlite_sequence"], tables))
rename_content = []
for table_name in tables:
    if table_name.startswith("Test_"):
        new_table_name = table_name.replace("Test_", "Task_")
        rename_content.append(f"ALTER TABLE {table_name} RENAME TO {new_table_name}")
    pass

script = "BEGIN;\n"
script += ";\n".join(rename_content) + ";\n"
script += "COMMIT;"
execute(script)

###########################################################################################
## Fix table Participants
###########################################################################################

# Prepare the part of the script which will fill the copy
user_ids = dict()
update_content = []
res = cur.execute(f"select * from Participants");
for user_idx, cur_row in enumerate(res, 1):
    user_id = cur_row['id']
    user_ids[user_id] = user_idx
    names = list(cur_row.keys())
    names.remove("id")
    values = []
    for n in names:
        if cur_row[n] is not None:
            values.append(f"'{cur_row[n]}'")
        else:
            values.append("NULL")
    update_content.append(f"insert into ParticipantsOther ({', '.join(names)}) values ({', '.join(values)})")


# Agglomerate the script
script = "BEGIN;\n"
script += """
CREATE TABLE IF NOT EXISTS "ParticipantsOther" (
	id INTEGER primary key autoincrement,
	conditions VARCHAR,
	study_id VARCHAR,
	session_id VARCHAR,
        user_id str
);

"""
script += ";\n".join(update_content) + ";\n"
script += "drop table Participants;\n";
script += "ALTER TABLE ParticipantsOther RENAME TO Participants;\n"
script += "COMMIT;"

# Execute the script
execute(script)


# Anonymize
script = "BEGIN;\n"
scripts += "update Participants set session_id=NULL;\n"
scripts += "update Participants set study_id=NULL;\n"
script += "COMMIT;"
execute(script)

###########################################################################################
## Fix other impacted tables
###########################################################################################
# List tables and remove the ones to not modify
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t["name"] for t in cur.fetchall()]
tables = list(filter(lambda x: x not in ["Participants", "Sample", "Administrators", "sqlite_sequence"], tables))

# Prepare scripts which 1. create a copy, 2. fill the copy, 3. drop the original. 4. rename the copy t be the original
update_content = []
for table_name in tables:
    res = cur.execute(f"select sql from sqlite_schema where type = 'table' and name = '{table_name}';")
    create_query = next(res)["sql"]
    create_query = create_query.replace(f'"{table_name}"', f'"{table_name}_copy"')
    create_query = create_query.replace("user_id VARCHAR", "user_id integer")

    update_content.append(create_query)

    res = cur.execute(f"select * from {table_name}");
    for cur_row in res:
        names = list(cur_row.keys())
        values = []
        for n in names:
            if n == "user_id":
                values.append(str(user_ids[cur_row[n]]))
            elif n.lower() == "freeform_feedback":
                values.append("NULL")
            elif cur_row[n] is not None:
                val = str(cur_row[n]).strip().replace("'", "''")
                values.append(f"'{val}'")
            else:
                values.append("NULL")
        update_content.append(f"insert into {table_name}_copy ({', '.join(names)}) values ({', '.join(values)})")

    update_content.append(f"drop table {table_name}")
    update_content.append(f"alter table {table_name}_copy rename to {table_name}")


# Execute the script
print("\n\n")
script = "BEGIN;\n"
script += ";\n".join(update_content) + ";\n"
script += "COMMIT;"
execute(script)

# We are done, close everything
cur.close()
con.close()
