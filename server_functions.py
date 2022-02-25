import os
import time
import boto3
import cred
from boto3.dynamodb.conditions import Key

root_directory = os.path.abspath(os.curdir)

session = boto3.Session(
    aws_access_key_id=cred.AWSAccessKeyId,
    aws_secret_access_key=cred.AWSSecretKey,
    region_name="us-east-2")
dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id=cred.AWSAccessKeyId,
                          aws_secret_access_key=cred.AWSSecretKey,
                          region_name="us-east-2")


def add_file_to_favorite_DB(username: str, file_name: str):
    table = dynamodb.Table('itoven_nottauserbase')
    username = username
    response = table.query(
        IndexName='Username_Index',
        KeyConditionExpression=Key('Username').eq(username)
    )
    u_id = response.get("Items")[0].get('User ID')
    u_name = response.get("Items")[0].get('Username')
    current_favorites = response.get("Items")[0].get('Favorites')
    print(f"Successfully added {file_name} to {username}'s favorites")
    response = table.update_item(
        Key={
            'User ID': u_id,
            'Username': u_name
        },
        UpdateExpression="set Favorites = :r",
        ExpressionAttributeValues={
            ':r': f"{current_favorites}\n{file_name}"
        },
        ReturnValues="UPDATED_NEW"
    )
    increase_popularity_index(file_name)
    return response


def remove_file_from_favorites_DB(username: str, file_name: str):
    table = dynamodb.Table('itoven_nottauserbase')
    username = username
    response = table.query(
        IndexName='Username_Index',
        KeyConditionExpression=Key('Username').eq(username)
    )
    u_id = response.get("Items")[0].get('User ID')
    u_name = response.get("Items")[0].get('Username')
    current_favorites = list(response.get("Items")[0].get('Favorites').split("\n"))
    for favorite in current_favorites:
        if favorite == '' or file_name:
            current_favorites.remove(favorite)
    current_favorites.remove(file_name)
    current_favorites = str(current_favorites).strip("[")
    current_favorites = current_favorites.strip("]")
    current_favorites = current_favorites.replace("'", '')
    current_favorites = current_favorites.replace("'", '')
    response = table.update_item(
        Key={
            'User ID': u_id,
            'Username': u_name
        },
        UpdateExpression="set Favorites = :r",
        ExpressionAttributeValues={
            ':r': current_favorites
        },
        ReturnValues="UPDATED_NEW"
    )
    print(f"Successfully removed {file_name} from {username}'s favorites list.")
    decrease_popularity_index(file_name)
    return response


def reset_user_favorites_DB(username: str):
    table = dynamodb.Table('itoven_nottauserbase')
    username = username
    response = table.query(
        IndexName='Username_Index',
        KeyConditionExpression=Key('Username').eq(username)
    )
    u_id = response.get("Items")[0].get('User ID')
    u_name = response.get("Items")[0].get('Username')
    response = table.update_item(
        Key={
            'User ID': u_id,
            'Username': u_name
        },
        UpdateExpression="set Favorites = :r",
        ExpressionAttributeValues={
            ':r': ""
        },
        ReturnValues="UPDATED_NEW"
    )
    print(f"Successfully reset {username}'s favorites list")
    return response


def get_favorites_list_user(username: str):
    try:
        table = dynamodb.Table('itoven_nottauserbase')
        username = username
        response = table.query(
            IndexName='Username_Index',
            KeyConditionExpression=Key('Username').eq(username)
        )
        u_id = response.get("Items")[0].get('User ID')
        u_name = response.get("Items")[0].get('Username')
        response = table.get_item(
            Key={
                'User ID': u_id,
                'Username': u_name
            })
        u_favorites = response.get("Item").get('Favorites')
        u_favorites = list(u_favorites.split("\n"))
        for item in u_favorites:
            if not item:
                u_favorites.remove(item)
        print(u_favorites)
        return u_favorites
    except:
        return ['test']


def increase_user_credit_count(username: str, credits_to_add: int):
    try:
        table = dynamodb.Table('itoven_nottauserbase')
        username = username
        response = table.query(
            IndexName='Username_Index',
            KeyConditionExpression=Key('Username').eq(username)
        )
        u_id = response.get("Items")[0].get('User ID')
        u_name = response.get("Items")[0].get('Username')
        current_credits = response.get("Items")[0].get('Credits')
        response = table.update_item(
            Key={
                'User ID': u_id,
                'Username': u_name
            },
            UpdateExpression="set Credits = :c",
            ExpressionAttributeValues={
                ':c': current_credits + credits_to_add
            },
            ReturnValues="UPDATED_NEW"
        )
        print(f"Added {credits_to_add} credits to {username}'s account")
        return response
    except:
        return False


def decrease_user_credit_count(username: str, credits_to_deduct: int):
    table = dynamodb.Table('itoven_nottauserbase')
    username = username
    response = table.query(
        IndexName='Username_Index',
        KeyConditionExpression=Key('Username').eq(username)
    )
    u_id = response.get("Items")[0].get('User ID')
    u_name = response.get("Items")[0].get('Username')
    current_credits = response.get("Items")[0].get('Credits')
    response = table.update_item(
        Key={
            'User ID': u_id,
            'Username': u_name
        },
        UpdateExpression="set Credits = :c",
        ExpressionAttributeValues={
            ':c': current_credits - credits_to_deduct
        },
        ReturnValues="UPDATED_NEW"
    )
    print(f"Deducted {credits_to_deduct} credits from {username}'s account")
    return response


# noinspection PyBroadException
def decrease_popularity_index(file_name: str):
    table = dynamodb.Table('itovenbucketdb2')
    file_name = file_name
    response = table.query(
        IndexName='FileDex',
        KeyConditionExpression=Key('File Name').eq(file_name)
    )
    file_id = response.get("Items")[0].get('ID')
    current_popularity = -1
    response = table.get_item(
        Key={
            'ID': file_id,
            'File Name': file_name})
    try:
        current_popularity = response.get("Items")[0].get("Popularity")
    except:
        print("No popularity points yet. Creating new attribute and setting it to 0.")
    if current_popularity > 0:
        response = table.update_item(
            Key={
                'ID': file_id,
                'File Name': file_name
            },
            UpdateExpression="set Popularity = :p",
            ExpressionAttributeValues={
                ':p': current_popularity - 1
            },
            ReturnValues="UPDATED_NEW"
        )
        print(f"Decreased the popularity of {file_name} to {current_popularity - 1}")
        return response
    else:
        response = table.update_item(
            Key={
                'ID': file_id,
                'File Name': file_name
            },
            UpdateExpression="set Popularity = :p",
            ExpressionAttributeValues={
                ':p': 0
            },
            ReturnValues="UPDATED_NEW"
        )
        print(f"Set the popularity of {file_name} to 0")
        return response


# noinspection PyBroadException
def increase_popularity_index(file_name: str):
    table = dynamodb.Table('itovenbucketdb2')
    file_name = file_name
    response = table.query(
        IndexName='FileDex',
        KeyConditionExpression=Key('File Name').eq(file_name)
    )
    file_id = response.get("Items")[0].get('ID')
    current_popularity = -1
    response = table.get_item(
        Key={
            'ID': file_id,
            'File Name': file_name})
    try:
        current_popularity = response.get("Items")[0].get("Popularity")
    except:
        print("No popularity points yet. Creating new attribute and setting it to 1.")
    if current_popularity > -1:
        response = table.update_item(
            Key={
                'ID': file_id,
                'File Name': file_name
            },
            UpdateExpression="set Popularity = :p",
            ExpressionAttributeValues={
                ':p': current_popularity + 1
            },
            ReturnValues="UPDATED_NEW"
        )
        print(f"Increased the popularity of {file_name} to {current_popularity + 1}")
        return response
    else:
        response = table.update_item(
            Key={
                'ID': file_id,
                'File Name': file_name
            },
            UpdateExpression="set Popularity = :p",
            ExpressionAttributeValues={
                ':p': 1
            },
            ReturnValues="UPDATED_NEW"
        )
        print(f"Increased the popularity of {file_name} to 1")
        return response


# Return text of text file in s3. We need to use this to check if file has been uploaded before.
def download_s3_text_file(x):
    # noinspection PyBroadException
    try:
        s3 = session.client('s3')
        my_bucket = 'itovenbucket'
        desired_file_name = x.split("/")[1]
        s3.download_file(my_bucket, x, desired_file_name)
        with open(desired_file_name) as f:
            contents = f.read()
        return contents
    except:
        pass


# Return text of text file in s3. We need to use this to check if file has been uploaded before.
def download_s3_text_file_prefix(x, prefix):
    # noinspection PyBroadException
    try:
        s3 = session.client('s3')
        my_bucket = 'itovenbucket'
        desired_file_name = x.split("/")[1]
        s3.download_file(my_bucket, x, f"{prefix}/{desired_file_name}")
        with open(desired_file_name) as f:
            contents = f.read()
        return contents
    except:
        pass


# returns a list of dictionaries
def get_DB_item_count():
    AWSAccessKeyId = cred.AWSAccessKeyId
    AWSSecretKey = cred.AWSSecretKey
    table1 = "itovenbucketdb2"
    response = dynamodb.describe_table(TableName=table1).get('Table').get('ItemCount')
    response = int(response)
    return response


def get_streamlined_file_list():
    return download_s3_text_file('special documents/itoven_file_list_one.txt').split(
        ", ")


# All MIDI Files in Bucket use a common 'prime' prefix. Local directory is a special place that the user may change
# noinspection PyBroadException
def download_MIDI_file(file_name: str, special_local_directory: str):
    # Then use the session to get the resource
    s3 = session.client('s3')
    my_bucket = 'itovenbucket'
    file_name = f"prime/{file_name}"
    desired_file_name = f"{special_local_directory}/{file_name.replace('prime/','')}"
    success = False
    s3.download_file(my_bucket, file_name, desired_file_name)
    print(f"Downloaded {file_name} as {desired_file_name}")
    increase_popularity_index(file_name.replace('prime/', ''))


def download_MIDI_file_temporary(file_name: str):
    # Then use the session to get the resource
    s3 = session.client('s3')
    # Clean up any other temporary files
    for file in os.listdir(root_directory):
        if ".MIDI" in file:
            if file != file_name:
                try:
                    os.remove(file)
                except:
                    pass
    my_bucket = 'itovenbucket'
    file_name = f"prime/{file_name}"
    desired_file_name = file_name.replace('prime/', '')
    s3.download_file(my_bucket, file_name, desired_file_name)
    increase_popularity_index(file_name.replace('prime/', ''))


def getDownloadsFolder():
    if os.name == 'nt':
        import ctypes
        from ctypes import windll, wintypes
        from uuid import UUID

        # ctypes GUID copied from MSDN sample code
        class GUID(ctypes.Structure):
            _fields_ = [
                ("Data1", wintypes.DWORD),
                ("Data2", wintypes.WORD),
                ("Data3", wintypes.WORD),
                ("Data4", wintypes.BYTE * 8)
            ]

            def __init__(self, uuidstr):
                uuid = UUID(uuidstr)
                ctypes.Structure.__init__(self)
                self.Data1, self.Data2, self.Data3, \
                    self.Data4[0], self.Data4[1], rest = uuid.fields
                for i in range(2, 8):
                    self.Data4[i] = rest>>(8-i-1)*8 & 0xff

        SHGetKnownFolderPath = windll.shell32.SHGetKnownFolderPath
        SHGetKnownFolderPath.argtypes = [
            ctypes.POINTER(GUID), wintypes.DWORD,
            wintypes.HANDLE, ctypes.POINTER(ctypes.c_wchar_p)
        ]

        def _get_known_folder_path(uuidstr):
            pathptr = ctypes.c_wchar_p()
            guid = GUID(uuidstr)
            if SHGetKnownFolderPath(ctypes.byref(guid), 0, 0, ctypes.byref(pathptr)):
                raise ctypes.WinError()
            return pathptr.value

        FOLDERID_Download = '{374DE290-123F-4565-9164-39C4925E467B}'
        return _get_known_folder_path(FOLDERID_Download)
    else:
        home = os.path.expanduser("~")
        return os.path.join(home, "Downloads")


print(getDownloadsFolder())