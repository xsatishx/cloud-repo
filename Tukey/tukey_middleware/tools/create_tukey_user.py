#!/usr/bin/env python
''' Account creation script from old tukey-middleware. Needs to be cleaned
up at some point '''

import logging
import optparse
import psycopg2

from tukey_middleware import local_settings

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
#logger.setLevel(logging.DEBUG)

verbose = False

def connect():
    conn_template = "dbname='%s' user='%s' host='%s' password='%s'"
    db_name = local_settings.AUTH_DB_NAME
    db_username = local_settings.AUTH_DB_USERNAME
    db_password = local_settings.AUTH_DB_PASSWORD
    host = local_settings.AUTH_DB_HOST

    connection = None

    try:
        conn_str = conn_template % (db_name, db_username, host, db_password)
        connection = psycopg2.connect(conn_str)

    except psycopg2.Warning as exc:
        logger.warning(exc.pgerror)

    except psycopg2.Error, exc:
        logger.error(exc.pgerror)

    return connection

def connect_and_query(cur, query):
    # only for queries no commit/rollback
    try:
        cur.execute(query)
        results = cur.fetchone()

    except StandardError as exc:
        logger.error(exc.pgerror)

    return results

def exists_query(cur, query):

    if verbose:
        print query

    return connect_and_query(cur, query)[0] > 0

def account_exists(cur, cloud, username):

    exists = """
    SELECT COUNT(id) FROM login, cloud
    where cloud_name='%(cloud)s' and username='%(username)s'
    and login.cloud_id = cloud.cloud_id;
    """ % locals()

    return exists_query(cur, exists)

def update_account(cloud, username, password):
    condition = """
    WHERE username='%(username)s' and
    cloud_id=(SELECT cloud_id FROM cloud WHERE cloud_name='%(cloud)s');
    """

    return [
        ("UPDATE login SET password='%(password)s' " + condition) % locals()
    ]

def account_enabled(cur, cloud, username):

    exists = """
    SELECT COUNT(id) FROM login_enabled, cloud, login
    where cloud_name='%(cloud)s' and username='%(username)s'
    and login.cloud_id = cloud.cloud_id
    and login.id = login_enabled.login_id;
    """ % locals()

    return exists_query(cur, exists)

def login_enabled(cur, method, identifier):

    exists = """SELECT COUNT(login_identifier_id) FROM
    login_identifier_enabled
    JOIN login_identifier ON login_identifier.id = login_identifier_enabled.login_identifier_id
    JOIN login_method ON login_method.method_id = login_identifier.method_id
    WHERE method_name='%(method)s' and identifier='%(identifier)s';""" % locals()

    return exists_query(cur, exists)

def enable_account(cloud, username):
    condition = """
    WHERE username='%(username)s' and
    cloud_id=(SELECT cloud_id FROM cloud WHERE cloud_name='%(cloud)s');
    """

    return [
        ("INSERT INTO login_enabled (login_id) SELECT id FROM login " + condition) % locals()
    ]

def create_account(cloud, username, password):

    return [
    "INSERT INTO userid DEFAULT VALUES;",
    """INSERT INTO login (userid, cloud_id, username, password)
    VALUES (currval('userid_userid_sequence'),
    (SELECT cloud_id FROM cloud WHERE cloud_name='%(cloud)s'),
    '%(username)s', '%(password)s');""" % locals()
    ]
def login_exists(cur, method, identifier):

    exists = """SELECT COUNT(id) FROM login_identifier
    JOIN login_method ON login_method.method_id = login_identifier.method_id
    WHERE method_name='%(method)s' and identifier='%(identifier)s';""" % locals()

    return exists_query(cur, exists)

def enable_login(method, identifier):
    return [
    """INSERT INTO login_identifier_enabled (login_identifier_id)
    SELECT id FROM login_identifier JOIN login_method
    ON login_method.method_id = login_identifier.method_id
    WHERE method_name='%(method)s' and identifier='%(identifier)s';""" % locals()
    ]

def create_login(method, identifier, cloud, username):
    return [
    """INSERT INTO login_identifier (userid, method_id, identifier)
    VALUES ((SELECT userid FROM login JOIN cloud ON login.cloud_id = cloud.cloud_id
        WHERE cloud_name='%(cloud)s' and username='%(username)s'),
    (SELECT method_id FROM login_method where method_name='%(method)s'),
     '%(identifier)s');""" % locals(),
    """INSERT INTO login_identifier_enabled (login_identifier_id)
    VALUES (currval('login_identifier_id_sequence'));""" % locals()
    ]

def add_account(cloud, username, password, method, identifier):

    return [
    """INSERT INTO login (userid, cloud_id, username, password)
    VALUES ((SELECT userid from login_identifier
    JOIN login_method on login_method.method_id = login_identifier.method_id
    WHERE method_name='%(method)s' and identifier='%(identifier)s'),
    (SELECT cloud_id FROM cloud WHERE cloud_name='%(cloud)s'),
    '%(username)s', '%(password)s');""" % locals()
    ]

# deletion statements
def disable_login(username, cloud):

    return ["""DELETE FROM login_enabled
        USING login, cloud WHERE login.id=login_enabled.login_id
        and login.cloud_id=cloud.cloud_id
        and login.username='%(username)s' and cloud.cloud_name='%(cloud)s';"""
        % locals()]

def delete_login(username, cloud):

    return ["""DELETE FROM login
        USING cloud WHERE login.cloud_id=cloud.cloud_id
        and login.username='%(username)s' and cloud.cloud_name='%(cloud)s';"""
        % locals()]

def disable_identifiers(username, cloud):

    return ["""DELETE FROM login_identifier_enabled
        USING login_identifier, login, cloud WHERE
        login_identifier.userid = login.userid
        and login.username = '%(username)s' and login.cloud_id = cloud.cloud_id
        and cloud.cloud_name = '%(cloud)s'
        and login_identifier.id = login_identifier_enabled.login_identifier_id;"""
        % locals()]

def delete_identifiers(username, cloud):

    return ["""DELETE FROM login_identifier
        USING login, cloud WHERE
        login_identifier.userid = login.userid
        and login.username = '%(username)s' and login.cloud_id = cloud.cloud_id
        and cloud.cloud_name = '%(cloud)s';"""
        % locals()]

def disable_identifier(identifier):

    return ["""DELETE FROM login_identifier_enabled
        USING login_identifier WHERE
        login_identifier.identifier='%(identifier)s'
        and login_identifier.id = login_identifier_enabled.login_identifier_id;"""
        % locals()]

def delete_identifier(identifier):

    return ["""DELETE FROM login_identifier
        WHERE login_identifier.identifier='%(identifier)s'"""
        % locals()]

def run_statements(statements):

    logger.debug(statements)

    conn = connect()
    cur = conn.cursor()

    try:
        for statement in statements:
            if verbose:
                print statement
            cur.execute(statement)

        conn.commit()

    except psycopg2.Warning, exc:
        logger.warning(exc.pgerror)
        conn.rollback()

    except psycopg2.Error, exc:
        logger.error(exc.pgerror)
        conn.rollback()

    finally:
        cur.close()
        conn.close()

def process_account(cloud, method, identifier, username, password):

    statements = []

    conn = connect()
    cur = conn.cursor()

    try:
        if account_exists(cur, cloud, username):
            # allow for changing password
            statements += update_account(cloud, username, password)
            if not account_enabled(cur, cloud, username):
                statements += enable_account(cloud, username)
        else:
            if login_exists(cur, method, identifier):
                statements += add_account(cloud, username, password, method,
                    identifier)
            else:
                statements += create_account(cloud, username, password)
            statements += enable_account(cloud, username)

        if login_exists(cur, method, identifier):
            if not login_enabled(cur, method, identifier):
                statements += enable_login(method, identifier)
        else:
            statements += create_login(method, identifier, cloud, username)

    except psycopg2.Warning, exc:
        logger.warning(exc.pgerror)

    except psycopg2.Error, exc:
        logger.error(exc.pgerror)

    finally:
        cur.close()
        conn.close()

    run_statements(statements)

def delete_account(cloud, username):

    run_statements(
        disable_identifiers(username, cloud) +
        delete_identifiers(username, cloud) +
        disable_login(username, cloud) +
        delete_login(username, cloud))

def disable_all():

    run_statements(["DELETE FROM login_enabled;",
        "DELETE FROM login_identifier_enabled;"])

if __name__ == "__main__":

    usage = """To create a user: %prog [-v] [cloud method identifer username password]
To disable all accounts: %prog [-v] -d
To delete a user: %prog [-v] -r [cloud username]"""

    parser = optparse.OptionParser(usage)

    parser.add_option("-d", "--disable-all",
        action="store_true", dest="disable_all")

    parser.add_option("-r", "--remove-user",
        action="store_true", dest="remove")

    parser.add_option("-v", "--verbose",
        action="store_true", dest="verbose")

    (options, args) = parser.parse_args()

    verbose = options.verbose

    if options.disable_all:
        if len(args) != 0:
            parser.error("incorrect number of arguments")
            exit(1)
        disable_all()

    elif options.remove:
        if len(args) != 2:
            parser.error("incorrect number of arguments")
            exit(1)
        delete_account(args[0], args[1])

    else:
        if len(args) != 5:
            parser.error("incorrect number of arguments")
            exit(1)

        process_account(args[0], args[1], args[2], args[3], args[4])

