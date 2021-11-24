import jwt

class jwtutil(object):

    def createToken(self):
        json = {
            "user_id": "root",
            "group_id": -1,
            "authentication": "MASTER"
        }

        return jwt.encode(json, "secret", algorithm="HS256")

    def tokenInfo(self, token):
        return jwt.decode(token, "secret", algorithms="HS256")

