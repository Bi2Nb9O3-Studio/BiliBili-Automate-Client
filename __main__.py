import prompt_toolkit
import asyncio,cli
from client import Client

def main():
    client=Client()
    client.run()

if __name__=="__main__":
    main()