import mysql.connector

# ---------------------------------
# DATABASE CONNECTION
# ---------------------------------
conn = mysql.connector.connect(
    host="localhost", user="root", password="Navaneesh@23", database="pygame"
)

cursor = conn.cursor()

# Disable safe updates for this session so we can update/delete by player_name
cursor.execute("SET SQL_SAFE_UPDATES = 0")


# ---------------------------------
# INSERT SCORE
# ---------------------------------
def insert_score(player_name, time_taken):

    # Check if player already exists
    check_sql = "SELECT id, time_taken FROM player_scores WHERE player_name=%s"
    cursor.execute(check_sql, (player_name,))
    result = cursor.fetchone()

    if result:
        # Player exists, update their score if the new time is better (lower)
        score_id, old_time = result
        best_time = min(old_time, time_taken)
        
        update_sql = "UPDATE player_scores SET time_taken=%s WHERE id=%s"
        cursor.execute(update_sql, (best_time, score_id))
    else:
        # New player, insert a new row
        insert_sql = """
        INSERT INTO player_scores (player_name, time_taken)
        VALUES (%s, %s)
        """
        cursor.execute(insert_sql, (player_name, time_taken))

    conn.commit()


# ---------------------------------
# GET TOP SCORES
# ---------------------------------
def get_top_scores(limit=5):

    sql = f"""
    SELECT id, player_name, time_taken
    FROM player_scores
    ORDER BY time_taken ASC
    LIMIT {limit}
    """

    cursor.execute(sql)

    return cursor.fetchall()


# ---------------------------------
# GET ALL SCORES
# ---------------------------------
def get_all_scores():

    cursor.execute(
        "SELECT id, player_name, time_taken "
        "FROM player_scores ORDER BY time_taken ASC"
    )

    return cursor.fetchall()


# ---------------------------------
# GET SCORE BY ID
# ---------------------------------
def get_score_by_id(score_id):

    sql = "SELECT player_name, time_taken FROM player_scores WHERE id=%s"
    cursor.execute(sql, (score_id,))
    return cursor.fetchone()

# ---------------------------------
# UPDATE SCORE
# ---------------------------------
def update_score(score_id, new_name, new_time):
    # Check if the new name belongs to another ID
    check_sql = "SELECT id FROM player_scores WHERE player_name=%s AND id != %s"
    cursor.execute(check_sql, (new_name, score_id))
    if cursor.fetchone():
        print(f"Error: The name '{new_name}' already exists in the database. Cannot create duplicates.")
        return False

    sql = """
    UPDATE player_scores
    SET player_name=%s, time_taken=%s
    WHERE id=%s
    """

    values = (new_name, new_time, score_id)

    cursor.execute(sql, values)

    conn.commit()
    return True


# ---------------------------------
# DELETE SCORE
# ---------------------------------
def delete_score(score_id):

    sql = """
    DELETE FROM player_scores
    WHERE id=%s
    """

    cursor.execute(sql, (score_id,))

    conn.commit()


# ---------------------------------
# TEST FUNCTIONS
# ---------------------------------
if __name__ == "__main__":

    print("\n=== ALL SCORES ===")
    print(f"{'ID':<5} | {'Player Name':<20} | {'Time Taken'}")
    print("-" * 45)
    all_scores = get_all_scores()
    for score in all_scores:
        print(f"{score[0]:<5} | {score[1]:<20} | {score[2]}")

    print("\n=== TOP SCORES ===")
    print(f"{'ID':<5} | {'Player Name':<20} | {'Time Taken'}")
    print("-" * 45)
    top_scores = get_top_scores()
    for score in top_scores:
        print(f"{score[0]:<5} | {score[1]:<20} | {score[2]}")
