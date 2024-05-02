from aiohttp import ClientSession
from asyncio import sleep
import aiofiles as aiof
import json
import os
import datetime as dt


from sqlalchemy.future import select

from db.models import Learner, Group
from db import session as create_db_session

# MAX_ID = 93933
# MAX_ID = 93933


DATA_DIR = r"D:\works\coding\python\school\E-Diary\data"


async def parse_learner_group_name(session: ClientSession, id: int):
    resp = await session.get(f"https://school.edu-penza.ru/learner/item/{id}/")
    data = await resp.json()
    if data["status"] == 200:
        group_id = data["returnedObject"]["group"]["id"]
        liter = data["returnedObject"]["group"]["name"]
        course = data["returnedObject"]["group"]["course"]

        db_session = await create_db_session()
        group = Group(group_id, course, liter)
        db_session.add(group)
        await db_session.commit()
        await db_session.close()
        print("save group")
        return group
    return None

async def parse_learner_group_id(session: ClientSession, id: int):
    resp = await session.get(f"https://school.edu-penza.ru/learner/item/{id}/")
    data = await resp.json()

    if data["status"] == 200:
        return data["returnedObject"]["group"]["id"]
    return None

async def parse_group(session: ClientSession, id: int):
    resp = await session.get(f"https://school.edu-penza.ru/subgroup/list/bygroup/{id}/content")
    data = await resp.json()
    if data["status"] == 200:
        async with aiof.open(os.path.join(DATA_DIR + r"\groups", f"{id}.json"), "w") as f:
            await f.write(json.dumps(data["returnedObject"], ensure_ascii=False))
            print("save group")
        for i in data["returnedObject"]:
            if i["name"].lower() == "весь класс":
                print("all class")
                group_id = await parse_learner_group_name(session, i["subgroupsContents"][0]["learner"]["id"])
                # print(group_id)
                db_session = await create_db_session()
                for student in i["subgroupsContents"]:
                    last_name, first_name = student["learner"]["lastAndFirstName"].split(" ")
                    person = (await db_session.execute(select(Learner).where(Learner.id == student["learner"]["id"]))).first()
                    if person:
                        person = person[0]
                        user_group_id = await parse_learner_group_id(session, person.id)
                        person.group_id = user_group_id
                    else:
                        db_session.add(Learner(student["learner"]["id"], group_id, first_name, last_name))
                    
                    print("add learner")
                await db_session.commit()
                await db_session.close()
                await sleep(2)
                break

async def parse_from_files(session: ClientSession):
    groups_files = os.listdir(os.getcwd() + "\data\groups")
    print(os.getcwd())
    for i in groups_files:
        async with aiof.open(os.path.join(DATA_DIR + r"\groups", f"{i}"), "r") as f:
            data = json.loads(await f.read())
        print(i)
        for i in data:
            if i["name"].lower() == "весь класс":
                print("all class")
                # group_id = await parse_learner_group_name(session, i["subgroupsContents"][0]["learner"]["id"])
                group = await parse_learner_group_name(session, i["subgroupsContents"][0]["learner"]["id"])
                db_session = await create_db_session()
                
                for student in i["subgroupsContents"]:
                    
                    last_name, first_name = student["learner"]["person"]["fullName"].split()[:2]
                    person = (await db_session.execute(select(Learner).where(Learner.id == student["learner"]["id"]))).scalar_one_or_none()
                    if person:
                        person = person
                        user_group_id = await parse_learner_group_id(session, person.id)
                        person.group_id = user_group_id
                    else:
                        learner = Learner(student["learner"]["id"], group.id, first_name, last_name)
                        db_session.add(learner)

                await db_session.commit()

async def add_born_date():
    groups_files = os.listdir(os.getcwd() + "\data\groups")
    for i in groups_files:
        async with aiof.open(os.path.join(DATA_DIR + r"\groups", f"{i}"), "r") as f:
            data = json.loads(await f.read())
        for i in data:
            if i["name"].lower() == "весь класс":
                db_session = await create_db_session()
                for student in i["subgroupsContents"]:
                    
                    born_date = dt.datetime.strptime(student["learner"]["person"]["bornDate"], "%Y-%m-%d")
                    person: Learner = (await db_session.execute(select(Learner).where(Learner.id == student["learner"]["id"]))).scalar_one()
                    person.birthday = born_date
                await db_session.commit()
                await db_session.close()

async def change_person_id():
    db_session = await create_db_session()
    for group in (await db_session.execute(select(Group))).scalars():
        async with aiof.open(os.path.join(DATA_DIR + r"\groups", f"{group.id}.json"), "r") as f:
            data = json.loads(await f.read())
        pupils = {}
        for i in data:
            if i["name"].lower() == "весь класс":
                for student in i["subgroupsContents"]:
                    pupils.update({student["learner"]["id"]: student["learner"]["person"]["id"]})                              
        for student in group.learner:
            student.person_id = pupils[student.id]
        
    await db_session.commit()