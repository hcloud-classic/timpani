LOGIN_QUERY= """
        query{
            login(username: "X_USERNAME", password: "X_PASSWORD"){
                token
            }
        }
    """

CHECKTOKEN_QUERY= """
        query{
            check_token(token: "X_TOKEN"){
                isvalid
                user_id
                group_id
                authentication
            }
        }
    """