import os
import sys
import pandas as pd
import psycopg2
from dotenv import load_dotenv

# Add project root to Python path
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

sys.path.append(PROJECT_ROOT)

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")

DATA_DIR = os.path.join(PROJECT_ROOT, "data")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def import_events(connection):
    file_path = os.path.join(DATA_DIR, "events.csv")

    df = pd.read_csv(file_path)

    print(f"Events CSV rows: {len(df)}")

    if df["event_id"].duplicated().any():
        raise ValueError("Duplicate event_id found in events.csv")

    cursor = connection.cursor()

    columns = [
        "event_id",
        "title",
        "description",
        "category",
        "subcategory",
        "tags",
        "event_type",
        "city",
        "state",
        "venue",
        "address",
        "latitude",
        "longitude",
        "start_date",
        "start_time",
        "end_date",
        "end_time",
        "price",
        "currency",
        "is_free",
        "organizer",
        "expected_attendees",
        "audience",
        "language",
        "rating"
    ]

    for _, row in df.iterrows():
        values = [row[column] for column in columns]

        is_free_index = columns.index("is_free")
        values[is_free_index] = bool(row["is_free"])
        
        cursor.execute(
            """
            INSERT INTO events (
                event_id,
                title,
                description,
                category,
                subcategory,
                tags,
                event_type,
                city,
                state,
                venue,
                address,
                latitude,
                longitude,
                start_date,
                start_time,
                end_date,
                end_time,
                price,
                currency,
                is_free,
                organizer,
                expected_attendees,
                audience,
                language,
                rating
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s
            )
            """,
            values
        )

    connection.commit()
    cursor.close()

    print("Events imported successfully.")


def import_queries(connection):
    file_path = os.path.join(DATA_DIR, "queries.csv")

    df = pd.read_csv(file_path)

    print(f"Queries CSV rows: {len(df)}")

    if df["query_id"].duplicated().any():
        raise ValueError("Duplicate query_id found in queries.csv")

    cursor = connection.cursor()

    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT INTO queries (
                query_id,
                query
            )
            VALUES (%s, %s)
            """,
            (
                row["query_id"],
                row["query"]
            )
        )

    connection.commit()
    cursor.close()

    print("Queries imported successfully.")


def import_relevance(connection):
    file_path = os.path.join(DATA_DIR, "relevance.csv")

    df = pd.read_csv(file_path)

    print(f"Relevance CSV rows: {len(df)}")

    cursor = connection.cursor()

    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT INTO relevance (
                query_id,
                event_id,
                relevance
            )
            VALUES (%s, %s, %s)
            """,
            (
                row["query_id"],
                row["event_id"],
                row["relevance"]
            )
        )

    connection.commit()
    cursor.close()

    print("Relevance judgments imported successfully.")


def main():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set in .env")

    connection = get_connection()

    try:
        print("Connected to PostgreSQL.")
        print()

        import_events(connection)
        import_queries(connection)
        import_relevance(connection)

        print()
        print("===================================")
        print("Dataset import completed successfully.")
        print("===================================")

    except Exception as error:
        connection.rollback()
        print("Import failed:")
        print(error)

    finally:
        connection.close()


if __name__ == "__main__":
    main()