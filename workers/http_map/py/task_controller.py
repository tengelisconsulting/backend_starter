from app import app
import ez


@ez.endpoint(route=b"/task/user-task/individual/create")
async def user_task_individual_create(
        user_id: str,
        title: str,
        desc: str
):
    res, _err = await app.ez.r(b"DB", b"/user_task_create", {
        "p_user_id": user_id,
        "p_task_type": "INDIVIDUAL",
        "p_title": title,
        "p_description": desc,
    })
    return (b"OK", res)


@ez.endpoint(route=b"/task/user-task/individual/update")
async def user_task_individual_update(
        user_id: str,
        task_id: str,
        completed: bool = None,
        title: str = None,
        desc: str = None
):
    res, _err = await app.ez.r(b"DB", b"/user_task_update", {
        "p_task_id": task_id,
        "p_completed": completed,
        "p_title": title,
        "p_description": desc,
    })
    return (b"OK", res)
