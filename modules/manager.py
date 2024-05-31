from modules import Database
from core import logger
from modules.bridger import bridge_batch


class Manager:
    @staticmethod
    async def run_module():
        try:
            logger.success(start_message, send_to_tg=False)
            module = input("Start module: ")

            if module == "1":
                database = Database.create_database()
                database.save_database()
            elif module == "2":
                await bridge_batch()
            else:
                logger.error(f"Invalid module number: {module}", send_to_tg=False)

        except KeyboardInterrupt:
            logger.error("Finishing script", send_to_tg=False)
        except Exception as e:
            logger.exception(str(e))


start_message = r"""
               __    _ __                        __                  
   _______  __/ /_  (_) /  _   __   ____  ____ _/ /______  ____  ___ 
  / ___/ / / / __ \/ / /  | | / /  /_  / / __ `/ //_/ __ \/ __ \/ _ \
 (__  ) /_/ / /_/ / / /   | |/ /    / /_/ /_/ / ,< / /_/ / / / /  __/   
/____/\__, /_.___/_/_/    |___/    /___/\__,_/_/|_|\____/_/ /_/\___/ 
     /____/      

1. Create database
2. Start bridger
"""
