from app.db.base import Base
from app.db.models import Book, Chapter, Highlight, ReviewCard, ReviewLog, Setting, SyncJob, User, UserNote
from app.db.session import engine


def main() -> None:
    # Import model classes above so SQLAlchemy registers every table.
    _ = (Book, Chapter, Highlight, ReviewCard, ReviewLog, Setting, SyncJob, User, UserNote)
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")


if __name__ == "__main__":
    main()
