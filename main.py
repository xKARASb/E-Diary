import asyncio
# from learners_parser.parser import *
from db import create_db
from TgBot import start_bot, stop_bot
from ITschool import learner_client

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def main():
    await create_db()
    await learner_client.start_polling()
    if asyncio.get_running_loop().is_running():
        await start_bot()

async def stop():
    await stop_bot()
    await learner_client.stop_polling()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        loop.run_until_complete(stop())
        loop.stop()
        loop.close()
        print("Exiting...")
        quit(1)
    except Exception as e:
        logging.info(e)
        quit(0)