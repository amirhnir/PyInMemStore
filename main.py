# Python Version: 3.8.3

from pyinmemstore import PyInMemStore

def main():
    print("Welcome to PyInMemStore!")
    store = PyInMemStore()
    print(store.HELP())

    while True:
        command = input("Enter a command or type 'EXIT' to quit: ").strip()

        if command == 'EXIT':
            print("Exiting PyInMemStore.")
            break

        result = store.execute_command(command)
        if result is not None:
            print(result)

if __name__ == "__main__":
    main()
