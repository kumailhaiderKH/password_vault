from .database import SessionLocal
from . import models, utils, config
from cryptography.fernet import Fernet

def rotate_keys():
    db = SessionLocal()
    try:
        passwords = db.query(models.user_vault).filter(models.user_vault.key_version != config.settings.current_key_version).all()
        print(f"Total passwords: {len(passwords)}")
        for p in passwords:
            key = utils.get_key_by_version(p.key_version)
            f = Fernet(key)
            decrypted = f.decrypt(p.platform_password.encode()).decode()
            print(f"decrypted: {decrypted}")
    
            # test encrypt directly
            current_key = utils.get_key_by_version(config.settings.current_key_version)
            print(f"current key: {current_key}")
            f2 = Fernet(current_key)
            re_encrypted = f2.encrypt(decrypted.encode()).decode()
            print(f"re-encrypted: {re_encrypted[:10]}...")
        for password in passwords:
            decrypted = utils.decrypt_password(password.platform_password, password.key_version)
            password.platform_password = utils.encrypt_password(decrypted)
            password.key_version = config.settings.current_key_version
        db.commit()
        print(f"Successfully rotated {len(passwords)} passwords ✅")
    except Exception as e:
        db.rollback()
        print(f"Rotation failed: {e}❌")

    finally:
        db.close()
if __name__ == "__main__":
    rotate_keys()

        

