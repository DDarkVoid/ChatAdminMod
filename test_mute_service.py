from app.database.database import Database
from app.services.mute_service import MuteService


def main():
    database = Database("test_secretar.db")
    mute_service = MuteService(database)

    connection_id = "TEST_CONNECTION"
    chat_id = 123456789

    print("=== TEST 1: mute forever ===")

    mute_service.mute(
        connection_id=connection_id,
        chat_id=chat_id
    )

    print(
        "Muted:",
        mute_service.is_muted(
            connection_id,
            chat_id
        )
    )

    print("\n=== TEST 2: unmute ===")

    mute_service.unmute(
        connection_id=connection_id,
        chat_id=chat_id
    )

    print(
        "Muted:",
        mute_service.is_muted(
            connection_id,
            chat_id
        )
    )

    print("\n=== TEST 3: mute for 5 minutes ===")

    mute_until = mute_service.mute(
        connection_id=connection_id,
        chat_id=chat_id,
        duration="5m"
    )

    print("Mute until:", mute_until)

    print(
        "Muted:",
        mute_service.is_muted(
            connection_id,
            chat_id
        )
    )

    database.close()


if __name__ == "__main__":
    main()