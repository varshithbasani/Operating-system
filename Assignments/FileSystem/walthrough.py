import time
from rich import print
from rich.table import Table
from rich.box import SIMPLE

from fileSystem import FileSystem

def execute_commands():
    
    fs = FileSystem()
    # ls command
    print("[bold blue]Command:[/bold blue] [green]ls[/green]")
    fs.list()
    fs.history.append('ls')
    promot=input("Enter any key to continue \n")

    # ls command
    print("[bold blue]Command:[/bold blue] [green]ls -la[/green]")
    fs.list(flag = ['l', 'a'])
    fs.history.append('ls -la')
    promot=input("Enter any key to continue \n")

    # mkdir command
    print("\n[bold blue]Command:[/bold blue] [green]mkdir newfolder[/green]")
    print(fs.mkdir(name='newfolder'))
    fs.history.append('mkdir newfolder')
    promot=input("Enter any key to continue \n")

    # ls command
    print("[bold blue]Command:[/bold blue] [green]ls -l[/green]")
    fs.list(flag = [ 'l'])
    fs.history.append('ls -l')
    promot=input("Enter any key to continue \n")

    # cd command
    print("\n[bold blue]Command:[/bold blue] [green]cd newfolder[/green]")
    fs.cd(path='newfolder')
    fs.history.append('cd newfolder')
    promot=input("Enter any key to continue \n")

    # pwd command
    print("\n[bold blue]Command:[/bold blue] [green]pwd[/green]")
    print(fs.pwd())
    fs.history.append('pwd')
    promot=input("Enter any key to continue \n")

    # cd command
    print("\n[bold blue]Command:[/bold blue] [green]cd ..[/green]")
    fs.cd(path='..')
    fs.history.append('cd ..')
    promot=input("Enter any key to continue \n")

    # pwd command
    print("\n[bold blue]Command:[/bold blue] [green]pwd[/green]")
    print(fs.pwd())
    fs.history.append('pwd')
    promot=input("Enter any key to continue \n")

    # rm command
    print("\n[bold blue]Command:[/bold blue] [green]rm -rf newfolder[/green]")
    print(fs.rm(name='newfolder', flags=['r', 'f']))
    fs.history.append('rm -rf newfolder')
    promot=input("Enter any key to continue \n")

    print("\n[bold blue]Command:[/bold blue] [green]ls -l Folder1[/green]")
    fs.list(path='Folder1', flag = ['l'])
    #time.sleep(2)
    promot=input("Enter any key to continue \n")

    # mv command
    print("\n[bold blue]Command:[/bold blue] [green]mv Folder1/file1 Folder2[/green]")
    print(fs.mv(source='Folder1/File1.txt', destination='Folder2'))
    fs.history.append('mv Folder1/File1 Folder2')
    promot=input("Enter any key to continue \n")

     # ls command
    print("\n[bold blue]Command:[/bold blue] [green]ls -l Folder1[/green]")
    fs.list(path='Folder1', flag = ['l'])
    #time.sleep(2)
    promot=input("Enter any key to continue \n")

    # ls command
    print("\n[bold blue]Command:[/bold blue] [green]ls -l Folder2[/green]")
    fs.list(path='Folder2', flag = ['l'])
    #time.sleep(2)
    promot=input("Enter any key to continue \n")

    # cp command
    print("\n[bold blue]Command:[/bold blue] [green]cp Folder2/File3 Folder4/newFile[/green]")
    print(fs.cp(source='Folder2/File3.txt', destination='Folder4/newFile.txt'))
    fs.history.append('cp Folder2/File3 Folder4/newFile')
    promot=input("Enter any key to continue \n")
    
    print("\n[bold blue]Command:[/bold blue] [green]ls -l Folder2[/green]")
    fs.list(path='Folder2', flag = ['l'])
    #time.sleep(2)
    promot=input("Enter any key to continue \n")

    print("\n[bold blue]Command:[/bold blue] [green]ls -l Folder4[/green]")
    fs.list(path='Folder4', flag = ['l'])
    #time.sleep(2)
    promot=input("Enter any key to continue \n")


     # history command
    print("\n[bold blue]Command:[/bold blue] [green]history[/green]")
    print(fs.get_history())
    fs.history.append('history')
    promot=input("Enter any key to continue \n")

    # cd command
    print("\n[bold blue]Command:[/bold blue] [green]cd Folder4[/green]")
    fs.cd(path='Folder4')
    fs.history.append('cd Folder4')
    promot=input("Enter any key to continue \n")

    # ls command
    print("\n[bold blue]Command:[/bold blue] [green]ls -l[/green]")
    fs.list(flag=['l'])
    fs.history.append('ls -l')
    promot=input("Enter any key to continue \n")

    # chmod command
    print("\n[bold blue]Command:[/bold blue] [green]chmod 777 File6.txt[/green]")
    print(fs.chmod(name='File6.txt', permission='777'))
    fs.history.append('chmod 777 File6.txt')
    promot=input("Enter any key to continue \n")

    # ls command
    print("\n[bold blue]Command:[/bold blue] [green]ls -l[/green]")
    fs.list(flag=['l'])
    fs.history.append('ls -l')
    promot=input("Enter any key to continue \n")

execute_commands()
