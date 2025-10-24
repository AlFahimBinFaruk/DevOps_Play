# seeder.py
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from sqlmodel import create_engine, Session, select
from sqlalchemy.orm import sessionmaker

# Import your models
from ..user.models import User
from ..todo.models import Todo
from ..test.models import Test
from ..core.security import hash_password  # Import your hash function

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_session():
    """Create a database session for seeding."""
    engine = create_engine(DATABASE_URL, echo=True)
    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine, class_=Session
    )
    return SessionLocal()


def seed_users():
    """Seed initial users."""
    db = get_db_session()
    try:
        # Check if users already exist
        existing_users = db.exec(select(User)).all()

        if len(existing_users) == 0:
            users_data = [
                {
                    "username": "admin",
                    "password": "admin123",
                },
                {"username": "testuser1", "password": "testpass123"},
                {
                    "username": "testuser2",
                    "password": "testpass123",
                },
            ]

            for user_data in users_data:
                # Hash the password before creating user
                hashed_password = hash_password(user_data["password"])

                user = User(
                    username=user_data["username"],
                    password=hashed_password,
                )

                db.add(user)

            db.commit()
            print("✅ Users seeded successfully!")
            print("📧 Admin credentials: admin / admin123")
            print(
                "🔑 Test user credentials: testuser1 / testpass123, testuser2 / testpass123"
            )
        else:
            print("ℹ️  Users already exist, skipping user seeding...")

    except Exception as e:
        print(f"❌ Error seeding users: {e}")
        db.rollback()
    finally:
        db.close()


def seed_todos():
    """Seed sample todos for existing users."""
    db = get_db_session()
    try:
        # Check if todos already exist
        existing_todos = db.exec(select(Todo)).all()

        if len(existing_todos) == 0:
            # Get some users to assign todos to
            users = db.exec(select(User)).all()

            if users:
                sample_todos = [
                    {
                        "title": "Complete project setup",
                        "description": "Set up FastAPI project with authentication",
                        "owner_id": users[0].id if users else None,
                    },
                    {
                        "title": "Implement user authentication",
                        "description": "Add JWT token-based authentication system",
                        "owner_id": users[0].id if users else None,
                    },
                    {
                        "title": "Create todo endpoints",
                        "description": "Build CRUD endpoints for todo management",
                        "owner_id": users[0].id if users else None,
                    },
                    {
                        "title": "Write documentation",
                        "description": "Document all API endpoints",
                        "owner_id": users[1].id if len(users) > 1 else users[0].id,
                    },
                    {
                        "title": "Add database seeding",
                        "description": "Create seeder script for initial data",
                        "owner_id": users[1].id if len(users) > 1 else users[0].id,
                    },
                ]

                for todo_data in sample_todos:
                    todo = Todo(
                        title=todo_data["title"],
                        description=todo_data["description"],
                        owner_id=todo_data["owner_id"],
                    )

                    db.add(todo)

                db.commit()
                print("✅ Sample todos seeded successfully!")
            else:
                print("❌ No users found. Please seed users first.")
        else:
            print("ℹ️  Todos already exist, skipping todo seeding...")

    except Exception as e:
        print(f"❌ Error seeding todos: {e}")
        db.rollback()
    finally:
        db.close()


def seed_admin_only():
    """Seed only admin user."""
    db = get_db_session()
    try:
        # Check if admin user exists
        admin_user = db.exec(select(User).where(User.username == "admin")).first()

        if not admin_user:
            admin = User(
                username="admin",
                password=hash_password("admin123"),
                email="admin@example.com",
                is_active=True,
                is_superuser=True,
                created_at=datetime.utcnow(),
            )

            db.add(admin)
            db.commit()
            print("✅ Admin user seeded successfully!")
            print("📧 Admin credentials: admin / admin123")
            print("⚠️  Please change the default password!")
        else:
            print("ℹ️  Admin user already exists, skipping...")

    except Exception as e:
        print(f"❌ Error seeding admin user: {e}")
        db.rollback()
    finally:
        db.close()


def run_all_seeders():
    """Run all seeders in proper order."""
    print("🌱 Starting database seeding...")
    print("-" * 50)

    # Seed in order (users first, then related data)
    seed_users()
    seed_todos()

    print("-" * 50)
    print("🎉 Database seeding completed!")


def clear_all_data():
    """Clear all data from tables (use with caution!)."""
    print("⚠️  WARNING: This will delete ALL data from your tables!")
    confirm = input("Are you sure you want to continue? (yes/no): ")

    if confirm.lower() == "yes":
        db = get_db_session()
        try:
            # Delete in reverse order to respect foreign keys
            db.exec(select(Todo)).delete()
            db.exec(select(Test)).delete()
            db.exec(select(User)).delete()

            db.commit()
            print("🗑️  All data cleared successfully!")

            # Ask if they want to reseed
            reseed = input("Would you like to seed fresh data? (yes/no): ")
            if reseed.lower() == "yes":
                run_all_seeders()

        except Exception as e:
            print(f"❌ Error clearing data: {e}")
            db.rollback()
        finally:
            db.close()
    else:
        print("❌ Operation cancelled.")


def show_usage():
    """Show available commands."""
    print("📋 Available seeder commands:")
    print("  python seeder.py all       - Run all seeders")
    print("  python seeder.py users     - Seed users only")
    print("  python seeder.py todos     - Seed todos only")
    print("  python seeder.py tests     - Seed test data only")
    print("  python seeder.py admin     - Seed admin user only")
    print("  python seeder.py clear     - Clear all data (dangerous!)")
    print("  python seeder.py help      - Show this help message")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ No command specified.")
        show_usage()
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "all":
        run_all_seeders()
    elif command == "users":
        seed_users()
    elif command == "todos":
        seed_todos()
    elif command == "admin":
        seed_admin_only()
    elif command == "clear":
        clear_all_data()
    elif command == "help":
        show_usage()
    else:
        print(f"❌ Unknown command: {command}")
        show_usage()
        sys.exit(1)
