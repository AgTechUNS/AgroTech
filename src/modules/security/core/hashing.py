import bcrypt

ROUNDS = 12


def hash_password(plain_password: str) -> str:
    if not plain_password:
        raise ValueError("La contraseña no puede estar vacía.")
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt(rounds=ROUNDS)).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def needs_rehash(hashed_password: str) -> bool:
    try:
        return hashed_password.count("$") < 4 or not hashed_password.startswith(f"$2b${ROUNDS:02d}$")
    except Exception:
        return True
