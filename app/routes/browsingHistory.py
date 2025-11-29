import sqlite3
import time

from flask import (
    Blueprint,
    render_template,
    session,
)
from settings import Settings
from utils.log import Log



browsingHistoryBlueprint = Blueprint("browsingHistory", __name__)


@browsingHistoryBlueprint.route("/browsinghistory")
def browsingHistory():
    if "userName" not in session:
        return render_template("unauthorized.html")

    userName = session["userName"]
    browsing_history = []

    try:
        # 连接到分析数据库获取浏览历史
        analytics_conn = sqlite3.connect(Settings.DB_ANALYTICS_ROOT)
        analytics_conn.set_trace_callback(Log.database)
        analytics_cursor = analytics_conn.cursor()

        # 获取用户的浏览历史记录，按时间倒序
        analytics_cursor.execute(
            """select postID, timeStamp from browsingHistory where userName = ? order by timeStamp desc """,
            (userName,)
        )
        history_records = analytics_cursor.fetchall()

        # 连接到文章数据库获取文章详情
        posts_conn = sqlite3.connect(Settings.DB_POSTS_ROOT)
        posts_conn.set_trace_callback(Log.database)
        posts_cursor = posts_conn.cursor()

        for record in history_records:
            postID = record[0]
            timeStamp = record[1]

            # 获取文章详情
            posts_cursor.execute(
                """select id, title, category, urlID from posts where id = ? """,
                (postID,)
            )
            post = posts_cursor.fetchone()

            if post:
                browsing_history.append({
                    "postID": post[0],
                    "title": post[1],
                    "category": post[2],
                    "urlID": post[3],
                    "timeStamp": timeStamp
                })

        posts_conn.close()
        analytics_conn.close()

    except Exception as e:
        Log.error(f"Error retrieving browsing history: {str(e)}")

    return render_template(
        "browsingHistory.html",
        browsing_history=browsing_history,
        appName=Settings.APP_NAME,
        now=int(time.time())
    )