import os
import sqlite3
from pathlib import Path


os.environ.setdefault("MPLCONFIGDIR", ".matplotlib-cache")

import matplotlib.pyplot as plt


DB_PATH = Path("data") / "events.db"
CHART_DIR = Path("charts")


def get_rows(conn, query):
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    return rows


def print_rows(title, rows):
    print("\n" + title)
    for row in rows:
        print(row)


def save_bar_chart(title, labels, values, file_name, y_max=None):
    plt.figure(figsize=(10, 5))
    bars = plt.bar(labels, values)
    plt.title(title)
    plt.xticks(rotation=30)

    if y_max:
        plt.ylim(0, y_max)

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            str(height),
            ha="center",
            va="bottom",
        )

    plt.tight_layout()
    plt.savefig(CHART_DIR / file_name)
    plt.close()


def save_pie_chart(title, labels, values, file_name):
    plt.figure(figsize=(7, 7))
    plt.pie(values, labels=labels, autopct="%1.1f%%")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(CHART_DIR / file_name)
    plt.close()


def analyze_event_type_counts(conn):
    query = """
    SELECT event_type, COUNT(*) AS count
    FROM events
    GROUP BY event_type
    ORDER BY count DESC;
    """

    rows = get_rows(conn, query)
    print_rows("1. 이벤트 타입별 발생 횟수", rows)

    labels = [row[0] for row in rows]
    values = [row[1] for row in rows]
    save_bar_chart("Event Type Counts", labels, values, "event_type_counts.png")


def analyze_top_purchase_users(conn):
    query = """
    SELECT t.user_id, COUNT(*) AS purchase_count
    FROM transactions t
    JOIN events e
        ON t.event_id = e.event_id
    WHERE e.event_type = 'PURCHASE'
    GROUP BY t.user_id
    ORDER BY purchase_count DESC
    LIMIT 3;
    """

    rows = get_rows(conn, query)
    print_rows("2. 구매 횟수가 가장 많은 유저 3명", rows)

    labels = [row[0] for row in rows]
    values = [row[1] for row in rows]
    save_bar_chart("Top 3 Purchase Users", labels, values, "top_purchase_users.png")


def analyze_product_review_rating(conn):
    query = """
    SELECT product, ROUND(AVG(review_rating), 2) AS avg_rating
    FROM reviews
    GROUP BY product
    ORDER BY product ASC;
    """

    rows = get_rows(conn, query)
    print_rows("3. 상품별 리뷰 평점", rows)

    labels = [row[0] for row in rows]
    values = [row[1] for row in rows]
    save_bar_chart(
        "Average Review Rating by Product",
        labels,
        values,
        "product_review_rating.png",
        5,
    )


def analyze_refund_ratio(conn):
    total_count = get_rows(conn, "SELECT COUNT(*) FROM events;")[0][0]
    refund_count = get_rows(conn, "SELECT COUNT(*) FROM events WHERE event_type = 'REFUND';")[0][0]
    not_refund_count = total_count - refund_count

    rows = [
        ("REFUND", refund_count),
        ("NOT_REFUND", not_refund_count),
    ]

    print_rows("4. 전체 이벤트 중 환불 비율", rows)

    labels = [row[0] for row in rows]
    values = [row[1] for row in rows]
    save_pie_chart("Refund Ratio", labels, values, "refund_ratio.png")


def analyze_top_amount_user_by_product(conn):
    query = """
    SELECT t.product, t.user_id, SUM(t.amount) AS total_amount
    FROM transactions t
    JOIN events e
        ON t.event_id = e.event_id
    WHERE e.event_type = 'PURCHASE'
    GROUP BY t.product, t.user_id
    ORDER BY t.product ASC, total_amount DESC;
    """

    all_rows = get_rows(conn, query)
    rows = []
    checked_products = []

    for row in all_rows:
        product = row[0]
        if product not in checked_products:
            rows.append(row)
            checked_products.append(product)

    print_rows("5. 상품별 구매액이 가장 높은 유저 1명", rows)

    labels = [row[0] + " / " + row[1] for row in rows]
    values = [row[2] for row in rows]
    save_bar_chart("Top Amount User by Product", labels, values, "top_amount_user_by_product.png")


def main():
    CHART_DIR.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    analyze_event_type_counts(conn)
    analyze_top_purchase_users(conn)
    analyze_product_review_rating(conn)
    analyze_refund_ratio(conn)
    analyze_top_amount_user_by_product(conn)

    conn.close()
    print("\n차트 이미지가 charts 폴더에 저장되었습니다.")


if __name__ == "__main__":
    main()
