from app import app
import ez


@ez.endpoint(route=b"/work-group/accept-invitation")
async def work_group_accept_invitation(
        user_id: str,
        group_id: str
):
    status, _err = await app.ez.r(b"DB", b"/user_work_group_status", {
        "p_user_id": user_id,
        "p_group_id": group_id,
    })
    if status == 1:
        return (b"OK", {"updated": 0})
    if status is None:
        return (b"ERR", {"code": 401,
                         "msg": "user was not invited to this group"})
    res, _err = await app.ez.r(b"DB", b"/user_work_group_join", {
        "p_user_id": user_id,
        "p_group_id": group_id,
    })
    return (b"OK", res)


@ez.endpoint(route=b"/work-group/invite")
async def work_group_invite(
        user_id: str,
        group_id: str,
        invite_email: str
):
    user_email, _err = await app.ez.r(b"DB", b"/get_user_email", {
        "p_user_id": user_id,
    })
    template, _err = await app.ez.r(b"MAIL_TEMPLATE", b"/get/GROUP_INVITE", {
        "inviter_email": user_email,
        "user_email": invite_email,
        "group_id": group_id,
    })
    invite_user, _err = await app.ez.r_json(b"DB", b"/get_user_slim", {
        "p_email": invite_email,
    })
    thread_rec, _err = await app.ez.r(b"USER_MAIL", b"/start_thread", {
        "user_id": invite_user["user_id"],
        "msg_type": "GROUP_INVITE",
        "subject": template["subject"],
        "body": template["body"],
        "adhoc": {},
    })
    return (b"OK", thread_rec)
