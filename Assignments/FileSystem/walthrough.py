import time
from rich import print
from rich.table import Table
from rich.box import SIMPLE

from fileSystem import FileSystem

def execute_commands():
    
    fs = FileSystem()
    # ls command
    print("[bold blue]Command:[/bold blue] [green]ls -lah[/green]")
    fs.list()
    # time.sleep(2)
    promot=input("Enter any key to continue \n")
    
    # ls command
    print("[bold blue]Command:[/bold blue] [green]ls -a[/green]")
    fs.list(flag = ['a'])
    #time.sleep(2)
    promot=input("Enter any key to continue \n")

    # mkdir command
    print("\n[bold blue]Command:[/bold blue] [green]mkdir newfolder[/green]")
    print(fs.mkdir(name='newfolder'))
    #time.sleep(2)
    promot=input("Enter any key to continue \n")

    # ls command
    print("\n[bold blue]Command:[/bold blue] [green]ls[/green]")
    fs.list()
    #time.sleep(2)
    promot=input("Enter any key to continue \n")

    # cd command
    print("\n[bold blue]Command:[/bold blue] [green]cd newfolder[/green]")
    fs.cd(path='newfolder')
    #time.sleep(2)
    promot=input("Enter any key to continue \n")

    # pwd command
    print("\n[bold blue]Command:[/bold blue] [green]pwd[/green]")
    print(fs.pwd())
    promot=input("Enter any key to continue \n")

    # cd command
    print("\n[bold blue]Command:[/bold blue] [green]cd ..[/green]")
    fs.cd(path='..')
    #time.sleep(2)
    promot=input("Enter any key to continue \n")

    # pwd command
    print("\n[bold blue]Command:[/bold blue] [green]pwd[/green]")
    print(fs.pwd())
    promot=input("Enter any key to continue \n")

    # rm command
    print("\n[bold blue]Command:[/bold blue] [green]rm -rf newfolder[/green]")
    print(fs.rm(name='newfolder', flags=['r', 'f']))
    #time.sleep(2)
    promot=input("Enter any key to continue \n")

    # ls command
    print("\n[bold blue]Command:[/bold blue] [green]ls[/green]")
    fs.list()
    #time.sleep(2)
    promot=input("Enter any key to continue \n")

    # mv command
    print("\n[bold blue]Command:[/bold blue] [green]mv Folder1 Folder2[/green]")
    print(fs.mv(source='Folder1', destination='Folder2'))
    promot=input("Enter any key to continue \n")
    
    # ls command
    print("\n[bold blue]Command:[/bold blue] [green]ls Folder2[/green]")
    fs.list(path='Folder2')
    #time.sleep(2)
    promot=input("Enter any key to continue \n")

    # cp command
    print("\n[bold blue]Command:[/bold blue] [green]cp Folder3 Folder4[/green]")
    print(fs.cp(source='Folder3', destination='Folder4'))
    #time.sleep(2)
    promot=input("Enter any key to continue \n")

    # ls command
    print("\n[bold blue]Command:[/bold blue] [green]ls Folder4[/green]")
    fs.list(path='Folder4')
    #time.sleep(2)
    promot=input("Enter any key to continue \n")

    # cd command
    print("\n[bold blue]Command:[/bold blue] [green]cd Folder4[/green]")
    fs.cd(path='Folder4')
    #time.sleep(2)
    promot=input("Enter any key to continue \n")

    # chmod command
    print("\n[bold blue]Command:[/bold blue] [green]chmod 777 File6.txt[/green]")
    print(fs.chmod(name='File6.txt', permission='777'))
    #time.sleep(2)
    promot=input("Enter any key to continue \n")

    # ls command
    print("\n[bold blue]Command:[/bold blue] [green]ls -l[/green]")
    fs.list(flag=['l'])
    #time.sleep(2)
    promot=input("Enter any key to continue \n")

execute_commands()