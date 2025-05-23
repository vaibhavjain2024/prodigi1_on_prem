from ldap3 import Server, Connection, ALL, NTLM, MODIFY_REPLACE
from app.config.config import LDAP_SERVER, IS_LDAP_DISABLE, TEMP_PASSWORD
from app.utils.cloudwatch_logs import log_to_cloudwatch
from app.utils.logger_utility import logger
from app.utils.decrypt_pwd import AES256

async def authenticate_ldap(username: str, user_password: str, ldap_bind: bool):
    if not "maruti\\" in username:
        username = f"maruti\\{username}"
    log_msg = f"IS_LDAP_DISABLE  authenticate_ldap : {IS_LDAP_DISABLE} for username {username}"
    logger.info(log_msg)
    print("****", ldap_bind)
    # log_to_cloudwatch("INFO", log_msg)
    if not bool(ldap_bind):
        if IS_LDAP_DISABLE:
            return True

    conn = None
    try:
        # user_password = AES256().decrypt(user_password)
        print("user_password *****", user_password)
        server = Server(LDAP_SERVER, get_info=ALL)
        conn = Connection(server, user=username, password=user_password, auto_bind=False)
        if conn.bind():
            whoami_result = conn.extend.standard.who_am_i()
            log_message = f"authenticate_ldap User DN: {whoami_result}"
            logger.info(log_message)
            # log_to_cloudwatch("INFO", log_message)
            return True
        else:
            log_message = "Failed to bind (authenticate) to the LDAP server."
            logger.info(log_message)
            # log_to_cloudwatch("INFO", log_message)
            return None
    except Exception as exc:
        log_message = f"authenticate_ldap Exception : {exc}"
        logger.info(log_message)
        # log_to_cloudwatch("INFO", log_message)
        return None
    finally:
        # Unbind the connection
        if conn and conn.bound:
            conn.unbind()


async def reset_password_ldap(user_dn: str, new_password: str):
    if not "maruti\\" in user_dn:
        user_dn = f"maruti\\{user_dn}"

    # user_dn = LDAP_USER_DN_TEMPLATE.format(username=username)
    conn = None
    if IS_LDAP_DISABLE: # for local testing
        return True

    try:
        decrypted_password = AES256().decrypt(new_password)
        server = Server(LDAP_SERVER, get_info=ALL)
        conn = Connection(server, user=user_dn, password=decrypted_password, auto_bind=True)

        conn.modify(user_dn, {'userPassword': [(MODIFY_REPLACE, [decrypted_password])]})

        if conn.result['result'] == 0:
            message = "Password reset successfully"
            logger.info(message)
            # log_to_cloudwatch("INFO", message)
            return True
        else:
            message = "Failed to reset password"
            logger.warning(message)
            # log_to_cloudwatch("WARNING", message)
            return None
    except Exception as e:
        message = f"An error occurred: {str(e)}"
        logger.error(message, exc_info=True)
        # log_to_cloudwatch("ERROR", message)
        return None
    finally:
        if conn and conn.bound:
            conn.unbind()