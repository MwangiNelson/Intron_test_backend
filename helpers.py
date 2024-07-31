import bcrypt

def generate_password_hash(password, salt_rounds=12):
    # Convert the password to bytes
    password_bytes = password.encode('utf-8')
    
    # Generate the salt and hash the password
    salt = bcrypt.gensalt(rounds=salt_rounds)
    password_hash = bcrypt.hashpw(password_bytes, salt)
    
    # Return the hash as a string
    return password_hash.decode('utf-8')