import sqlite3
from datetime import datetime, timedelta

from flask import (
    Blueprint,
    render_template,
    session,
)
from settings import Settings
from utils.log import Log
from utils.time import currentTimeStamp

browsingHistoryBlueprint = Blueprint("browsingHistory", __name__)


@browsingHistoryBlueprint.route("/browsing-history")
def browsingHistory():
    if "userName" not in session:
        # Redirect to login page if user is not logged in
        return render_template("login.html")

    userName = session["userName"]
    current_time = currentTimeStamp()
    # Calculate timestamp for one month ago
    one_month_ago = current_time - (30 * 24 * 60 * 60)

    # Get browsing history for the user from the last month
    Log.database(f"Connecting to '{Settings.DB_ANALYTICS_ROOT}' database")
    connection = sqlite3.connect(Settings.DB_ANALYTICS_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()

    cursor.execute(
        """select postID, timeStamp from browsingHistory where userName = ? and timeStamp >= ? order by timeStamp desc """,
        (userName, one_month_ago),
    )
    browsing_history = cursor.fetchall()

    connection.close()

    # Get post details for each browsing history entry
    posts = []
    if browsing_history:
        Log.database(f"Connecting to '{Settings.DB_POSTS_ROOT}' database")
        connection = sqlite3.connect(Settings.DB_POSTS_ROOT)
        connection.set_trace_callback(Log.database)
        cursor = connection.cursor()

        for entry in browsing_history:
            postID = entry[0]
            timeStamp = entry[1]

            cursor.execute(
                """select id, title, category, urlID from posts where id = ? """,
                (postID,),
            )
            post = cursor.fetchone()

            if post:
                posts.append({
                    "id": post[0],
                    "title": post[1],
                    "category": post[2],
                    "urlID": post[3],
                    "timeStamp": timeStamp
                })

        connection.close()

    return render_template(
        "browsingHistory.html",
        posts=posts,
        appName=Settings.APP_NAME
    )