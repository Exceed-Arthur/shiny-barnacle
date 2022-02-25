import time
import boto3
import cred
from boto3.dynamodb.conditions import Key


def get_formatted_time_elapsed(x):
    starter = x
    seconds1 = time.time() - starter
    seconds2 = seconds1 % 60
    minutes = int((seconds1 / 60) % 60)
    hours = int((seconds1 / 60 / 60))
    timer = f"(Time elapsed: {hours}h:{minutes}m:{round(seconds2, 4)}s)"
    return timer


def get_favorites_list_user(username: str):
    try:
        session = boto3.Session(
            aws_access_key_id=cred.AWSAccessKeyId,
            aws_secret_access_key=cred.AWSSecretKey,
            region_name="us-east-2")
        dynamodb = boto3.resource('dynamodb',
                                  aws_access_key_id=cred.AWSAccessKeyId,
                                  aws_secret_access_key=cred.AWSSecretKey,
                                  region_name="us-east-2")
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

        return u_favorites
    except AttributeError:
        return "None"


def get_membership_status_user(username: str):
    session = boto3.Session(
        aws_access_key_id=cred.AWSAccessKeyId,
        aws_secret_access_key=cred.AWSSecretKey,
        region_name="us-east-2")
    dynamodb = boto3.resource('dynamodb',
                              aws_access_key_id=cred.AWSAccessKeyId,
                              aws_secret_access_key=cred.AWSSecretKey,
                              region_name="us-east-2")
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
    u_membership = response.get("Item").get('Membership')
    if not u_membership:
        return "Free Version Only. Visit the activation to activate full version."
    elif u_membership not in ["Gold", "Silver"]:
        return "Free Version Only. Visit the activation to activate full version."
    else:
        return u_membership


def cancel_membership(username: str):
    change_days(username, 'reset')  # Set days until new credits back to 30
    session = boto3.Session(
        aws_access_key_id=cred.AWSAccessKeyId,
        aws_secret_access_key=cred.AWSSecretKey,
        region_name="us-east-2")
    dynamodb = boto3.resource('dynamodb',
                              aws_access_key_id=cred.AWSAccessKeyId,
                              aws_secret_access_key=cred.AWSSecretKey,
                              region_name="us-east-2")
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
    response = table.update_item(
        Key={
            'User ID': u_id,
            'Username': u_name
        },
        UpdateExpression="set Membership = :m",
        ExpressionAttributeValues={
            ':m': "Free"
        },
        ReturnValues="UPDATED_NEW"
    )


# Arg str: Reset, decrease (+++ or +-)
def change_days(username: str, change: str):
    session = boto3.Session(
        aws_access_key_id=cred.AWSAccessKeyId,
        aws_secret_access_key=cred.AWSSecretKey,
        region_name="us-east-2")
    dynamodb = boto3.resource('dynamodb',
                              aws_access_key_id=cred.AWSAccessKeyId,
                              aws_secret_access_key=cred.AWSSecretKey,
                              region_name="us-east-2")
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
    u_Days = response.get("Item").get('Days')  # Days until adding more credits.
    if change.lower() == "reset":
        response = table.update_item(
            Key={
                'User ID': u_id,
                'Username': u_name
            },
            UpdateExpression="set Days = :d",
            ExpressionAttributeValues={
                ':d': 30
            },
            ReturnValues="UPDATED_NEW"
        )
        return response
    elif change.lower() == "decrease":
        response = table.update_item(
            Key={
                'User ID': u_id,
                'Username': u_name
            },
            UpdateExpression="set Days = :d",
            ExpressionAttributeValues={
                ':d': int(u_Days) - 1
            },
            ReturnValues="UPDATED_NEW"
        )
        return response


# Check remaining days until more credits
def get_days_remaining(username: str):
    session = boto3.Session(
        aws_access_key_id=cred.AWSAccessKeyId,
        aws_secret_access_key=cred.AWSSecretKey,
        region_name="us-east-2")
    dynamodb = boto3.resource('dynamodb',
                              aws_access_key_id=cred.AWSAccessKeyId,
                              aws_secret_access_key=cred.AWSSecretKey,
                              region_name="us-east-2")
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
    u_Days = response.get("Item").get('Days')  # Days until adding more credits.
    return u_Days


def increase_user_credit_count(username: str, credits_to_add: int):
    session = boto3.Session(
        aws_access_key_id=cred.AWSAccessKeyId,
        aws_secret_access_key=cred.AWSSecretKey,
        region_name="us-east-2")
    dynamodb = boto3.resource('dynamodb',
                              aws_access_key_id=cred.AWSAccessKeyId,
                              aws_secret_access_key=cred.AWSSecretKey,
                              region_name="us-east-2")
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
            ':c': int(current_credits) + credits_to_add
        },
        ReturnValues="UPDATED_NEW"
    )
    print(f"Added {credits_to_add} credits to {username}'s account")
    return response


def decrease_user_credit_count(username: str, credits_to_deduct: int):
    session = boto3.Session(
        aws_access_key_id=cred.AWSAccessKeyId,
        aws_secret_access_key=cred.AWSSecretKey,
        region_name="us-east-2")
    dynamodb = boto3.resource('dynamodb',
                              aws_access_key_id=cred.AWSAccessKeyId,
                              aws_secret_access_key=cred.AWSSecretKey,
                              region_name="us-east-2")
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


def get_user_credit_count(username: str):
    session = boto3.Session(
        aws_access_key_id=cred.AWSAccessKeyId,
        aws_secret_access_key=cred.AWSSecretKey,
        region_name="us-east-2")
    dynamodb = boto3.resource('dynamodb',
                              aws_access_key_id=cred.AWSAccessKeyId,
                              aws_secret_access_key=cred.AWSSecretKey,
                              region_name="us-east-2")
    table = dynamodb.Table('itoven_nottauserbase')
    username = username
    response = table.query(
        IndexName='Username_Index',
        KeyConditionExpression=Key('Username').eq(username)
    )
    u_id = response.get("Items")[0].get('User ID')
    u_name = response.get("Items")[0].get('Username')
    current_credits = response.get("Items")[0].get('Credits')
    if response:
        return str(current_credits)
    else:
        return "0"


def get_platypus(username: str):
    session = boto3.Session(
        aws_access_key_id=cred.AWSAccessKeyId,
        aws_secret_access_key=cred.AWSSecretKey,
        region_name="us-east-2")
    dynamodb = boto3.resource('dynamodb',
                              aws_access_key_id=cred.AWSAccessKeyId,
                              aws_secret_access_key=cred.AWSSecretKey,
                              region_name="us-east-2")
    table = dynamodb.Table('itoven_nottauserbase')
    username = username
    response = table.query(
        IndexName='Username_Index',
        KeyConditionExpression=Key('Username').eq(username)
    )
    platypus = response.get("Items")[0].get('Platypus')


def user_exists(username: str):
    session = boto3.Session(
        aws_access_key_id=cred.AWSAccessKeyId,
        aws_secret_access_key=cred.AWSSecretKey,
        region_name="us-east-2")
    dynamodb = boto3.resource('dynamodb',
                              aws_access_key_id=cred.AWSAccessKeyId,
                              aws_secret_access_key=cred.AWSSecretKey,
                              region_name="us-east-2")
    table = dynamodb.Table('itoven_nottauserbase')
    username = username
    try:
        response = table.query(
            IndexName='Username_Index',
            KeyConditionExpression=Key('Username').eq(username))
        if "@" and "." in response:
            return True
        else:
            return False
    except:
        return False


def daily_pro_account_checkup():
    starter = time.time()
    session = boto3.Session(
        aws_access_key_id=cred.AWSAccessKeyId,
        aws_secret_access_key=cred.AWSSecretKey,
        region_name="us-east-2")
    dynamodb = boto3.resource('dynamodb',
                              aws_access_key_id=cred.AWSAccessKeyId,
                              aws_secret_access_key=cred.AWSSecretKey,
                              region_name="us-east-2")
    table = dynamodb.Table('itoven_nottauserbase')
    list_of_members = []
    try:
        response = table.query(
            IndexName='MemberUserDex',
            KeyConditionExpression=Key('Membership').eq('Gold'))
        temp_list = response.get('Items')
        for attribute_set in temp_list:
            username_mini = attribute_set.get('Username')
            membership_mini = attribute_set.get('Membership')
            # Get each Gold User and add to pro list
            list_of_members.append({username_mini: membership_mini})
    except:
        print("Failed to Retrieve Gold Users. Try again.")
        return False
    try:
        response = table.query(
            IndexName='MemberUserDex',
            KeyConditionExpression=Key('Membership').eq('Silver'))
        temp_list = response.get('Items')
        for attribute_set in temp_list:
            username_mini = attribute_set.get('Username')
            membership_mini = attribute_set.get('Membership')  # Get each silver member and add to pro member list
            # Get each Gold User and add to pro list
            list_of_members.append({username_mini: membership_mini})
    except:
        print("Failed to Retrieve Silver Users. Try again.")
        return False
    secondary_member_list = get_from_email_txns('/Users/celeryman/Downloads/Download.CSV')
    for pro_user_pair in list_of_members:
        change_days(pro_user_pair[0], 'decrease')  # Decrease the number of days until more credits arrive
        if get_days_remaining(pro_user_pair[0]) < 0:
            if pro_user_pair[0] in secondary_member_list:
                if pro_user_pair[1].lower() == "gold":
                    change_days(pro_user_pair[0], 'reset')
                    increase_user_credit_count(pro_user_pair[0], 1000)
                elif pro_user_pair[1].lower() == "silver":
                    change_days(pro_user_pair[0], 'reset')
                    increase_user_credit_count(pro_user_pair[0], 500)
    print(
        f"Successfully completed daily check up of pro users and gave people their credits! {get_formatted_time_elapsed(starter)}")


def activate_subscription(username: str, tier: str):
    if tier in ["Gold", "Silver"]:
        session = boto3.Session(
            aws_access_key_id=cred.AWSAccessKeyId,
            aws_secret_access_key=cred.AWSSecretKey,
            region_name="us-east-2")
        dynamodb = boto3.resource('dynamodb',
                                  aws_access_key_id=cred.AWSAccessKeyId,
                                  aws_secret_access_key=cred.AWSSecretKey,
                                  region_name="us-east-2")
        table = dynamodb.Table('itoven_nottauserbase')
        username = username
        response = table.query(
            IndexName='Username_Index',
            KeyConditionExpression=Key('Username').eq(username)
        )
        u_id = response.get("Items")[0].get('User ID')
        response = table.update_item(
            Key={
                'User ID': u_id,
                'Username': username
            },
            UpdateExpression="set Membership = :m",
            ExpressionAttributeValues={
                ':m': tier
            },
            ReturnValues="UPDATED_NEW"
        )
        if tier == "Gold":
            increase_user_credit_count(username=username, credits_to_add=1000)
        elif tier == "Silver":
            increase_user_credit_count(username=username, credits_to_add=500)
        change_days(username=username, change='reset')  # Set credit renewal timer to 30 days
        return response


def upgrade_subscription(username: str):
    cancel_membership(username=username)
    activate_subscription(username=username, tier="Gold")


# Download CSV of Transactions first. Then call it. You need to remember to download it every day.
def get_from_email_txns(path_to_csv):
    data = []
    pro_members1 = []
    pro_members = []
    with open(path_to_csv, 'r') as file:
        data = file.readlines()
    for line in data:
        if line != "\n":
            if line != "":
                if line != "From Email Address":
                    pro_members1.append(line.split(",")[10])
    for value in pro_members1:
        if value:
            pro_members.append(value.strip('"'))
    for member in pro_members:
        if member == '':
            pro_members.remove(member)
    for member in pro_members:
        if member == '':
            pro_members.remove(member)
    pro_members.remove('From Email Address')
    for member in pro_members:
        if "@" not in member:
            pro_members.remove(member)
    return pro_members


def get_DB_item_count(table: str):
    AWSAccessKeyId = cred.AWSAccessKeyId
    AWSSecretKey = cred.AWSSecretKey
    dynamodb = boto3.client(
        service_name='dynamodb',
        region_name="us-east-2",
        aws_access_key_id=AWSAccessKeyId,
        aws_secret_access_key=AWSSecretKey
    )
    response = dynamodb.describe_table(TableName=table).get('Table').get('ItemCount')
    response = int(response)
    return response


def create_dyno_acct(username: str, platypus: str):
    AWSAccessKeyId = cred.AWSAccessKeyId
    AWSSecretKey = cred.AWSSecretKey
    table = 'itoven_nottauserbase'
    dynamodb = boto3.client(
        service_name='dynamodb',
        region_name="us-east-2",
        aws_access_key_id=AWSAccessKeyId,
        aws_secret_access_key=AWSSecretKey
    )
    username = username
    response = dynamodb.Table(table).query(
        IndexName='Username_Index',
        KeyConditionExpression=Key('Username').eq(username)
    )
    if not response:
        dynamodb = boto3.resource(
            service_name='dynamodb',
            region_name="us-east-2",
            aws_access_key_id=AWSAccessKeyId,
            aws_secret_access_key=AWSSecretKey
        )
        response = dynamodb.Table(table).put_item(
            Item={
                'User ID': get_DB_item_count(table) + 1,
                'Username': username,
                'Platypus': platypus,
                'Days': 30,
                'Membership': 'Free',
                'Favorites': '',
                'Credits': 200,
            }
        )
        print(f"Successfully created DynamoDB item for {username}'s account.")


def txt_file_to_list(file: str):
    data = []
    with open(file, 'r') as f:
        data = f.read().replace("\n", ',')
    data = data.split(",")
    return data


def user_authenticated(username: str, passion: str):
    if user_exists(username=username):
        if passion == get_platypus(username=username):
            return True
    else:
        return False


def download_s3(file, desired_file_name):
    session = boto3.Session(
        aws_access_key_id=cred.AWSAccessKeyId,
        aws_secret_access_key=cred.AWSSecretKey,
        region_name="us-east-2")
    s3 = session.client('s3')
    my_bucket = 'itovenbucket'
    s3.download_file(my_bucket, file, desired_file_name)
