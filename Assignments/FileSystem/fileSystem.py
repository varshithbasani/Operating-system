# Filesystem Starter Class

from sqliteCRUD import SQLiteCrud
from prettytable import PrettyTable


class FileSystem:
    def __init__(self,db_name=None):
        if not db_name:
            self.db_name = "filesystem.sqlite"
        else:
            self.db_name = db_name
        self.crud = SQLiteCrud(self.db_name)
        self.cwd = "/home/user"
        self.cwdid = 0


    def __getParentId(self, current_id):
        """Get the ID of the parent directory given the current directory's ID.

        Args:
            current_id (int): The ID of the current directory.

        Returns:
            int or None: The ID of the parent directory if found, or None if not found.
        """
        try:
            # Query the database to find the parent directory's ID
            query = "SELECT pid FROM files_data WHERE id = ?;"
            self.crud.cursor.execute(query, (current_id,))
            result = self.crud.cursor.fetchone()
            if result:
                parent_id = result[0]
                return parent_id
            else:
                return None

        except Exception as e:
            print(f"error: {e}")
        
    def __getPathId(self, path):
        """Get the ID of a file or directory based on a given path.

        Args:
            path (str): The path to the file or directory, which can be absolute or relative.

        Returns:
            int or None: The ID of the file or directory if found, or None if not found.
        """
        # Initialize the parent_id as the root directory's ID

        if path.startswith("/home/user"):
            parent_id = 0
            path = path.replace("/home/user", "")
        else:
            parent_id = self.cwdid
        path = path.strip()
        # if path is ..
        if path == "..":
            parent_id = self.__getParentId(parent_id)
            return parent_id 
        # Split the path into parts based on '/' to navigate the directory structure
        path_parts = path.split('/')

        # Iterate through the path parts to find the target file or directory
        for part in path_parts:
            if not part or part == '.':
                # Skip empty path parts
                continue

            if part == "..":
                # Move to the parent directory by finding its ID
                parent_id = self.__getParentId(parent_id)
            else:
                query = f"SELECT id FROM files_data WHERE name = ? AND pid = ?;"
                self.crud.cursor.execute(query, (part, parent_id))
                result = self.crud.cursor.fetchone()
                if result:
                    parent_id = result[0]
                else:
                    return None
                
        # Return the ID of the target file or directory
        return parent_id

    def __formatted_results(self, results):
        """Format results as a PrettyTable."""
        table = PrettyTable()
        headers = [desc[0] for desc in self.crud.cursor.description]
        for i in range(len(headers)):
            if headers[i] == "size":
                headers[i] += " (KB)"
        table.field_names = headers
        table.add_rows(results)
        return table
    
    def __convert_digit(self, digit):
        """
        Convert a single digit (0-7) into its 'rwx' equivalent.

        Args:
            digit (int): A single digit (0-7).

        Returns:
            str: The 'rwx' equivalent representation.
        """
        if digit < 0 or digit > 7:
            raise ValueError("Invalid digit. Must be between 0 and 7.")

        permission_map = {
            0: '---',
            1: '--x',
            2: '-w-',
            3: '-wx',
            4: 'r--',
            5: 'r-x',
            6: 'rw-',
            7: 'rwx',
        }

        return permission_map[digit]

    def __convert_permission(self, triple):
        """
        Convert a triple of numbers (e.g., 644) into the 'rwx' equivalent (e.g., 'rw-r--r--').
        
        Args:
            triple (int): A triple of numbers representing permissions (e.g., 644).

        Returns:
            str: The 'rwx' equivalent representation (e.g., 'rw-r--r--').
        """
        if triple < 0 or triple > 777:
            raise ValueError("Invalid permission triple. Must be between 0 and 777.")

        # Convert each digit of the triple to its 'rwx' equivalent
        owner = self.__convert_digit(triple // 100)
        group = self.__convert_digit((triple // 10) % 10)
        others = self.__convert_digit(triple % 10)

        return owner + group + others
        
    def list(self,**kwargs):
        """ List the files and folders in current directory

        Params:
            path (string) : path to folder
            flag (list) : flags as a list of strings (e.g., ["l", "a"])
        """
        # try:
        path = kwargs.get("path")
        flag = kwargs.get("flag")
        query = f"SELECT name, owner, created_date, size, type FROM files_data WHERE pid = ? AND name NOT LIKE '.%'; "
        if flag:
            if "l" in flag:
                query = f"SELECT id, pid, name, created_date, modified_date, size, type, owner, groop, permissions FROM files_data WHERE pid = ?"
            elif "a" in flag:
                query = query.replace(" AND name NOT LIKE '.%'", "")
        if path:
            cwdid = self.__getPathId(path=path)
            if cwdid:
                self.crud.cursor.execute(query, (cwdid,))
            else:
                return "Invalid path."
        else:
            self.crud.cursor.execute(query, (self.cwdid,))
        result = self.crud.cursor.fetchall()
        if result:
            print(self.__formatted_results(result))
        else:
            print(f"Directory is empty.")
        # except Exception as e:
        #     print(f"error: {e}")

    def chmod(self,**kwargs):
        """ Change the permissions of a file
            1) will need the file / folder id
            2) select permissions from the table where that id exists
            3) 
        Params:
            id (int) :  id of file or folder
            permission (string) : +x -x 777 644

            if its a triple just overwrite or update table 

        Example:
            +x 
            p = 'rw-r-----'
            p[2] = x
            p[5] = x
            p[8] = x

        """
        try:
            name = kwargs.get("name")
            id = self.__getPathId(path=name)
            permission = kwargs.get("permission")
            if permission.isdigit():
                permission = self.__convert_permission(int(permission))
                self.crud.update_data("files_data", 'permissions', permission, 'id', id)
            else:
                # read the current permissions
                query = f"SELECT permissions FROM files_data WHERE id = ?;"
                self.crud.cursor.execute(query, (id,))
                result = self.crud.cursor.fetchone()
                if result:
                    current_permissions = result[0]
                    # change the permissions
                    if permission == "+x":
                        current_permissions = current_permissions[:2] + "x" + current_permissions[3:5] + "x" + current_permissions[6:8] + "x"
                    elif permission == "-x":
                        current_permissions = current_permissions[:2] + "-" + current_permissions[3:5] + "-" + current_permissions[6:8] + "-"
                    elif permission == "+r":
                        current_permissions = 'r' + current_permissions[1:3] + 'r' + current_permissions[4:6] + 'r' + current_permissions[7:]
                    elif permission == "-r":
                        current_permissions = '-' + current_permissions[1:3] + '-' + current_permissions[4:6] + '-' + current_permissions[7:]
                    elif permission == "+w":
                        current_permissions = current_permissions[:1] + 'w' + current_permissions[2:4] + 'w' + current_permissions[5:7] + 'w' + current_permissions[8:]
                    elif permission == "-w":
                        current_permissions = current_permissions[:1] + '-' + current_permissions[2:4] + '-' + current_permissions[5:7] + '-' + current_permissions[8:]
                    else:
                        return "Invalid permission."
                    # update the table
                    self.crud.update_data("files_data", 'permissions', current_permissions, 'id', id)
            return "Permissions updated successfully."
        except Exception as e:
            return f"error: {e}"

    def cd(self,**kwargs):
        """
        cd .. = move to parent directory from cwd
        cd ../.. 
        cd /root  (need to find id of that folder, and set swd )
        cd homework/english (involves a check to make sure folder exist)
        """
        try:
            path = kwargs.get("path")
            if not path:
                return "Invalid path."
            path = path.strip('/')
            cwdid = self.__getPathId(path=path)

            if cwdid is not None:
                self.cwdid = cwdid
                if path.startswith("/home/user"):
                    curr_path = ""
                else:
                    curr_path = self.cwd
                for part in path.split("/"):
                    if part == "..":
                        curr_path = "/".join(curr_path.split("/")[:-1])
                    elif part == ".":
                        continue
                    else:
                        curr_path += "/" + part

                self.cwd = curr_path
            else:
                print("Invalid path.")
                return
            print(f"Current directory changed to '{self.cwd}'.")
        except Exception as e:
            print(f"error: {e}")
        
    def mkdir(self,**kwargs):
        """
            create a folder in the current directory

        """
        try:
            name = kwargs.get("name")
            if not name:
                return "Invalid folder name."
            query = f"SELECT id FROM files_data WHERE name = ? AND pid = ?;"
            self.crud.cursor.execute(query, (name, self.cwdid))
            result = self.crud.cursor.fetchone()
            if result:
                return f"Folder '{name}' already exists in the current directory."
            else:
                # Insert data into the table
                query = f"INSERT INTO files_data (pid, name, created_date, modified_date, size, type, owner, groop, permissions) VALUES (?, ?, datetime('now'), datetime('now'), 0, 'folder', 'user1', 'group1', 'rwxr-xr-x');"
                self.crud.cursor.execute(query, (self.cwdid, name))
                # self.crud.conn.commit()
                return f"Folder '{name}' created successfully."
        except Exception as e:
            return f"error: {e}"
    
    def pwd(self):
        """get the current working directory."""
        return f"Current Directory: {self.cwd}"  

    def rm(self,**kwargs):
        """Remove files or folders from the current directory.

        Args:
            name (str): The name of the file or folder to remove.
            flags (list): A list of flags to modify the behavior of the command.
                f - Force removal of the file or folder.
                r - Recursively remove the file or folder and all of its contents.
        """
        try:
            name = kwargs.get("name")
            flags = kwargs.get("flags")
            if not name:
                return "Invalid file or folder name."
            id = self.__getPathId(path=name)
            if id is not None:
                # Check if the target is a file or folder
                query = f"SELECT type FROM files_data WHERE id = ?;"
                self.crud.cursor.execute(query, (id,))
                result = self.crud.cursor.fetchone()
                if result:
                    target_type = result[0]
                    if target_type == 'folder':
                        # Check if the folder is empty
                        query = f"SELECT count(*) FROM files_data WHERE pid = ?;"
                        self.crud.cursor.execute(query, (id,))
                        result = self.crud.cursor.fetchone()
                        count = result[0]
                        if (count >= 1 and flags and 'r' in flags) or count == 0:
                            # Delete the folder and all of its contents
                            query = f"DELETE FROM files_data WHERE id = ? OR pid = ?;"
                            self.crud.cursor.execute(query, (id, id))
                            # self.crud.conn.commit()
                            return f"Folder '{name}' deleted successfully."
                        else:
                            return f"Folder '{name}' is not empty."
                    else:
                        if 'f' in flags:
                            # Delete the file
                            query = f"DELETE FROM files_data WHERE id = ?;"
                            self.crud.cursor.execute(query, (id,))
                            # self.crud.conn.commit()
                            return f"File '{name}' deleted successfully."
                        else:
                            return f"use -f flag to delete file '{name}'."
                else:
                    return f"File or folder '{name}' not found in the current directory."
            else:
                return f"File or folder '{name}' not found in the current directory."
        except Exception as e:
            return f"error: {e}"

    def mv(self,**kwargs):
        """Move a file or folder to a new location.

        Args:
            source (str): The name of the file or folder to move.
            destination (str): The destination path to move the file or folder to.
        """
        try:
            source = kwargs.get("source")
            destination = kwargs.get("destination")
            if not source or not destination:
                return "Invalid source or destination."
            source_id = self.__getPathId(path=source)
            destination_id = self.__getPathId(path=destination)
            if source_id is not None and destination_id is not None:
                # Check if the destination is a folder
                query = f"SELECT type FROM files_data WHERE id = ?;"
                self.crud.cursor.execute(query, (destination_id,))
                result = self.crud.cursor.fetchone()
                if result:
                    destination_type = result[0]
                    if destination_type == 'folder':
                        # Move the file or folder to the destination
                        query = f"UPDATE files_data SET pid = ? WHERE id = ?;"
                        self.crud.cursor.execute(query, (destination_id, source_id))
                        # self.crud.conn.commit()
                        return f"File or folder '{source}' moved to '{destination}'."
                    else:
                        return f"Destination '{destination}' is not a folder."
                else:
                    return f"Destination '{destination}' not found."
            else:
                return f"File or folder not found. Please check the inputs and try again."
        except Exception as e:
            return f"error: {e}"

    def cp(self, **kwargs):
        """Copy a file or folder to a new location.

        Args:
            source (str): The name of the file or folder to copy.
            destination (str): The destination path to copy the file or folder to.
        """
        try:
            source = kwargs.get("source")
            destination = kwargs.get("destination")
            if not source or not destination:
                return "Invalid source or destination."
            source_id = self.__getPathId(path=source)
            destination_id = self.__getPathId(path=destination)
            if source_id is not None and destination_id is not None:
                # Check if the destination is a folder
                query = f"SELECT type FROM files_data WHERE id = ?;"
                self.crud.cursor.execute(query, (destination_id,))
                result = self.crud.cursor.fetchone()
                if result:
                    destination_type = result[0]
                    if destination_type == 'folder':
                        # get the source data
                        query = f"SELECT * FROM files_data WHERE id = ?;"
                        self.crud.cursor.execute(query, (source_id,))
                        result = self.crud.cursor.fetchone()

                        if result:
                            # Insert file or folder into the destination
                            query = f"INSERT INTO files_data (pid, name, created_date, modified_date, size, type, owner, groop, permissions) VALUES (?, ?, datetime('now'), datetime('now'), ?, ?, ?, ?, ?);"
                            self.crud.cursor.execute(query, (destination_id, result[2], result[5], result[6], result[7], result[8], result[9]))
                            copied_name = result[2]
                            # get copied file or folder id
                            query = f"SELECT id FROM files_data WHERE name = ? AND pid = ?;"
                            self.crud.cursor.execute(query, (result[2], destination_id))
                            copied_id = self.crud.cursor.fetchone()[0]
                            # if source is a folder
                            if result[6] == 'folder':
                                # copy content of folder to destination
                                query = f"SELECT * FROM files_data WHERE pid = ?;"
                                self.crud.cursor.execute(query, (source_id,))
                                result = self.crud.cursor.fetchall()
                                if result:
                                    for row in result:
                                        if row[6] == 'folder':
                                            # print(f"{source}/{row[2]}", f"{destination}/{result[2]}")
                                            self.cp(source=f"{source}/{row[2]}", destination=f"{destination}/{copied_name}")
                                        else:
                                            # Insert the file into the destination
                                            query = f"INSERT INTO files_data (pid, name, created_date, modified_date, size, type, owner, groop, permissions) VALUES (?, ?, datetime('now'), datetime('now'), ?, ?, ?, ?, ?);"
                                            self.crud.cursor.execute(query, (copied_id, row[2], row[5], row[6], row[7], row[8], row[9]))

                                    # self.crud.conn.commit()
                                    return f"File or folder '{source}' copied to '{destination}'."
                                else:
                                    return f"File or folder '{source}' not found."
                            else:
                                return f"File or folder '{source}' copied to '{destination}'."
                        else:
                            return f"Destination '{destination}' is not a folder."
                else:
                    return f"Destination '{destination}' not found."
            else:
                return f"File or folder not found. Please check the inputs and try again."
        except Exception as e:
            return f"error: {e}"


# Example usage:
if __name__ == "__main__":
    """
    THIS USAGE REALLY JUST SHOWS THE SqliteCRUD CLASS BUT WITH A FILESYSTEM THEME.
    WILL FIX AS WE ADD FUNCTIONALITY INTO THE FileSystem CLASS ABOVE
    SORRY FOR ALL CAPS DIDN'T WANT YOU TO MISS    
    """
     # Define table schema
    table_name = "files_data"
    columns = ["id INTEGER PRIMARY KEY", "pid INTEGER", "name TEXT", "created_date TEXT", "modified_date TEXT", "size REAL","type TEXT","owner TEXT","groop TEXT","permissions TEXT", "content BLOB"]
    # Load table
    test_data = [
        (1, 0, 'Folder1', '2023-09-25 10:00:00', '2023-09-25 10:00:00', 20.0, 'folder', 'user1', 'group1', 'rwxr-xr-x', None),
        (2, 1, 'File1.txt', '2023-09-25 10:15:00', '2023-09-25 10:15:00', 1024.5, 'file', 'user1', 'group1', 'rw-r--r--', 'This is the content of File1.txt'),
        (3, 1, 'File2.txt', '2023-09-25 10:30:00', '2023-09-25 10:30:00', 512.0, 'file', 'user2', 'group2', 'rw-rw-r--', 'This is the content of File2.txt'),
        (4, 0, 'Folder2', '2023-09-25 11:00:00', '2023-09-25 11:00:00', 0.0, 'folder', 'user2', 'group2', 'rwxr-xr--', None),
        (5, 4, 'File3.txt', '2023-09-25 11:15:00', '2023-09-25 11:15:00', 2048.75, 'file', 'user3', 'group3', 'rw-r--r--', 'This is the content of File3.txt'),
        (6, 4, 'File4.txt', '2023-09-25 11:30:00', '2023-09-25 11:30:00', 4096.0, 'file', 'user3', 'group3', 'rw-r--r--', 'This is the content of File4.txt'),
        (7, 0, 'Folder3', '2023-09-25 12:00:00', '2023-09-25 12:00:00', 0.0, 'folder', 'user4', 'group4', 'rwxr-x---', None),
        (8, 7, 'File5.txt', '2023-09-25 12:15:00', '2023-09-25 12:15:00', 8192.0, 'file', 'user4', 'group4', 'rw-------', 'This is the content of File5.txt'),
        (9, 0, 'Folder4', '2023-09-25 13:00:00', '2023-09-25 13:00:00', 0.0, 'folder', 'user5', 'group5', 'rwxr-xr-x', None),
        (10, 9, 'File6.txt', '2023-09-25 13:15:00', '2023-09-25 13:15:00', 3072.25, 'file', 'user5', 'group5', 'rwxr-xr--', 'This is the content of File6.txt'),
        (11, 0, '.new.txt', '2023-09-25 13:15:00', '2023-09-25 13:15:00', 3072.25, 'file', 'user5', 'group5', 'rwxr-xr--', 'This is the content of File6.txt'),

    ]

    conn = SQLiteCrud("filesystem.sqlite")

    conn.drop_table(table_name)

    conn.create_table(table_name, columns)
    print(conn.describe_table(table_name))

    for row in test_data:
        conn.insert_data(table_name, row)
    conn.conn.commit()
    print(conn.formatted_print(table_name))
