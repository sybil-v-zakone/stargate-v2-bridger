import asyncio

from modules import Manager


async def main():
    await Manager.run_module()


if __name__ == "__main__":
    asyncio.run(main())
