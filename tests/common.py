import logging

import framework as fmk


def create_user(
        email: str,
        password: str
) -> str:
    logging.info("creating user %s", email)
    user_id = fmk.req("/auth/account/new", method="POST", data={
        "email": email,
        "password": password,
        "timezone": fmk.t.timezone,
    })
    return user_id


def login(
        email: str,
        password: str
) -> None:
    token_res = fmk.req("/auth/authenticate/username-password", method="POST",
                        data={
                            "email": email, "password": password
                        })
    token = token_res["session_token"]
    fmk.t.s.headers["Authorization"] = "Bearer: {}".format(token)
    return None


async def reset_user_and_session():
    logging.info("resetting test user")
    ok, user_id = await fmk.ez("DB", "/get_user_id", {
        "p_email": fmk.TEST_EMAIL
    })
    logging.info("loaded user id: %s", user_id)
    if b"OK" != ok:
        raise fmk.TestFailure(user_id)
    if user_id:
        logging.info("deleting test user")
        ok, deleted = await fmk.ez("DB", "/fetch/val", {
            "sql": "SELECT ac_user_delete(p_user_id => $1::UUID)",
            "bindargs": [user_id]
        })
        if b"OK" != ok:
            raise fmk.TestFailure(deleted)
    create_user(fmk.TEST_EMAIL, fmk.TEST_PW)
    logging.info("logging in")
    login(fmk.TEST_EMAIL, fmk.TEST_PW)
    return
