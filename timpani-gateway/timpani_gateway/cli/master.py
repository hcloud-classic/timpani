import bcrypt
import hashlib
import click
from ..nameko.api import ApimanagerClient

apimanager_client = ApimanagerClient()

def masteraccount(username, password):
    print("username : {}, password : {}".format(username, password))
    Hash_sha256 = hashlib.sha256(password.encode('utf-8'))
    print("HASH : {}".format(Hash_sha256.hexdigest()))
    new_salt = bcrypt.gensalt()
    bcrypthash = bcrypt.hashpw(Hash_sha256.hexdigest().encode('utf-8'), new_salt)
    print("BCRYPT HASH : {}".format(bcrypthash.decode('utf-8')))
    res = apimanager_client.logincheck(username, bcrypthash.decode('utf-8'))
    print(res)


@click.command()
@click.option('--username', help="Master User ID")
@click.option('--password', help="Master User Password")
def main(username, password):
    print("username : {}, password : {}".format(username, password))
    masteraccount(username, password)


if __name__ == "__main__":
    main()

