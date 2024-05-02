import asyncio
# from learners_parser.parser import *
from db import create_db
from TgBot import start_bot
from ITschool import learner_client

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# async def main():
#     print("main")
#     await create_db()
    # teacher_jsessionid = "E6CDB5542E939349A8854D0DCB8C842D"
    
    # cookies = {
    #     "JSESSIONID": teacher_jsessionid,
    # }

async def main():
    await create_db()
    await learner_client.start_polling()
    await start_bot()


if __name__ == "__main__":
    asyncio.run(main())
    