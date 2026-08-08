import werkzeug.security as security

def hash_password(password: str) -> str:
    return security.generate_password_hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return security.check_password_hash(password_hash, password)
