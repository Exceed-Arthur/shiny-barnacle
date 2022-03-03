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
    dynamodb = boto3.resource(
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

def txt_file_to_listv2(file: str):
    data = ['0815.ru', '0wnd.net', '0wnd.org', '10minutemail.co.za', '10minutemail.com', '123-m.com', '1fsdfdsfsdf.tk', '1pad.de', '20minutemail.com', '21cn.com', '2fdgdfgdfgdf.tk', '2prong.com', '30minutemail.com', '33mail.com', '3trtretgfrfe.tk', '4gfdsgfdgfd.tk', '4warding.com', '5ghgfhfghfgh.tk', '6hjgjhgkilkj.tk', '6paq.com', '7tags.com', '9ox.net', 'a-bc.net', 'agedmail.com', 'ama-trade.de', 'amilegit.com', 'amiri.net', 'amiriindustries.com', 'anonmails.de', 'anonymbox.com', 'antichef.com', 'antichef.net', 'antireg.ru', 'antispam.de', 'antispammail.de', 'armyspy.com', 'artman-conception.com', 'azmeil.tk', 'baxomale.ht.cx', 'beefmilk.com', 'bigstring.com', 'binkmail.com', 'bio-muesli.net', 'bobmail.info', 'bodhi.lawlita.com', 'bofthew.com', 'bootybay.de', 'boun.cr', 'bouncr.com', 'breakthru.com', 'brefmail.com', 'bsnow.net', 'bspamfree.org', 'bugmenot.com', 'bund.us', 'burstmail.info', 'buymoreplays.com', 'byom.de', 'c2.hu', 'card.zp.ua', 'casualdx.com', 'cek.pm', 'centermail.com', 'centermail.net', 'chammy.info', 'childsavetrust.org', 'chogmail.com', 'choicemail1.com', 'clixser.com', 'cmail.net', 'cmail.org', 'coldemail.info', 'cool.fr.nf', 'courriel.fr.nf', 'courrieltemporaire.com', 'crapmail.org', 'cust.in', 'cuvox.de', 'd3p.dk', 'dacoolest.com', 'dandikmail.com', 'dayrep.com', 'dcemail.com', 'deadaddress.com', 'deadspam.com', 'delikkt.de', 'despam.it', 'despammed.com', 'devnullmail.com', 'dfgh.net', 'digitalsanctuary.com', 'dingbone.com', 'disposableaddress.com', 'disposableemailaddresses.com', 'disposableinbox.com', 'dispose.it', 'dispostable.com', 'dodgeit.com', 'dodgit.com', 'donemail.ru', 'dontreg.com', 'dontsendmespam.de', 'drdrb.net', 'dump-email.info', 'dumpandjunk.com', 'dumpyemail.com', 'e-mail.com', 'e-mail.org', 'e4ward.com', 'easytrashmail.com', 'einmalmail.de', 'einrot.com', 'eintagsmail.de', 'emailgo.de', 'emailias.com', 'emaillime.com', 'emailsensei.com', 'emailtemporanea.com', 'emailtemporanea.net', 'emailtemporar.ro', 'emailtemporario.com.br', 'emailthe.net', 'emailtmp.com', 'emailwarden.com', 'emailx.at.hm', 'emailxfer.com', 'emeil.in', 'emeil.ir', 'emz.net', 'ero-tube.org', 'evopo.com', 'explodemail.com', 'express.net.ua', 'eyepaste.com', 'fakeinbox.com', 'fakeinformation.com', 'fansworldwide.de', 'fantasymail.de', 'fightallspam.com', 'filzmail.com', 'fivemail.de', 'fleckens.hu', 'frapmail.com', 'friendlymail.co.uk', 'fuckingduh.com', 'fudgerub.com', 'fyii.de', 'garliclife.com', 'gehensiemirnichtaufdensack.de', 'get2mail.fr', 'getairmail.com', 'getmails.eu', 'getonemail.com', 'giantmail.de', 'girlsundertheinfluence.com', 'gishpuppy.com', 'gmial.com', 'goemailgo.com', 'gotmail.net', 'gotmail.org', 'gotti.otherinbox.com', 'great-host.in', 'greensloth.com', 'grr.la', 'gsrv.co.uk', 'guerillamail.biz', 'guerillamail.com', 'guerrillamail.biz', 'guerrillamail.com', 'guerrillamail.de', 'guerrillamail.info', 'guerrillamail.net', 'guerrillamail.org', 'guerrillamailblock.com', 'gustr.com', 'harakirimail.com', 'hat-geld.de', 'hatespam.org', 'herp.in', 'hidemail.de', 'hidzz.com', 'hmamail.com', 'hopemail.biz', 'ieh-mail.de', 'ikbenspamvrij.nl', 'imails.info', 'inbax.tk', 'inbox.si', 'inboxalias.com', 'inboxclean.com', 'inboxclean.org', 'infocom.zp.ua', 'instant-mail.de', 'ip6.li', 'irish2me.com', 'iwi.net', 'jetable.com', 'jetable.fr.nf', 'jetable.net', 'jetable.org', 'jnxjn.com', 'jourrapide.com', 'jsrsolutions.com', 'kasmail.com', 'kaspop.com', 'killmail.com', 'killmail.net', 'klassmaster.com', 'klzlk.com', 'koszmail.pl', 'kurzepost.de', 'lawlita.com', 'letthemeatspam.com', 'lhsdv.com', 'lifebyfood.com', 'link2mail.net', 'litedrop.com', 'lol.ovpn.to', 'lolfreak.net', 'lookugly.com', 'lortemail.dk', 'lr78.com', 'lroid.com', 'lukop.dk', 'm21.cc', 'mail-filter.com', 'mail-temporaire.fr', 'mail.by', 'mail.mezimages.net', 'mail.zp.ua', 'mail1a.de', 'mail21.cc', 'mail2rss.org', 'mail333.com', 'mailbidon.com', 'mailbiz.biz', 'mailblocks.com', 'mailbucket.org', 'mailcat.biz', 'mailcatch.com', 'mailde.de', 'mailde.info', 'maildrop.cc', 'maileimer.de', 'mailexpire.com', 'mailfa.tk', 'mailforspam.com', 'mailfreeonline.com', 'mailguard.me', 'mailin8r.com', 'mailinater.com', 'mailinator.com', 'mailinator.net', 'mailinator.org', 'mailinator2.com', 'mailincubator.com', 'mailismagic.com', 'mailme.lv', 'mailme24.com', 'mailmetrash.com', 'mailmoat.com', 'mailms.com', 'mailnesia.com', 'mailnull.com', 'mailorg.org', 'mailpick.biz', 'mailrock.biz', 'mailscrap.com', 'mailshell.com', 'mailsiphon.com', 'mailtemp.info', 'mailtome.de', 'mailtothis.com', 'mailtrash.net', 'mailtv.net', 'mailtv.tv', 'mailzilla.com', 'makemetheking.com', 'manybrain.com', 'mbx.cc', 'mega.zik.dj', 'meinspamschutz.de', 'meltmail.com', 'messagebeamer.de', 'mezimages.net', 'ministry-of-silly-walks.de', 'mintemail.com', 'misterpinball.de', 'moncourrier.fr.nf', 'monemail.fr.nf', 'monmail.fr.nf', 'monumentmail.com', 'mt2009.com', 'mt2014.com', 'mycard.net.ua', 'mycleaninbox.net', 'mymail-in.net', 'mypacks.net', 'mypartyclip.de', 'myphantomemail.com', 'mysamp.de', 'mytempemail.com', 'mytempmail.com', 'mytrashmail.com', 'nabuma.com', 'neomailbox.com', 'nepwk.com', 'nervmich.net', 'nervtmich.net', 'netmails.com', 'netmails.net', 'neverbox.com', 'nice-4u.com', 'nincsmail.hu', 'nnh.com', 'no-spam.ws', 'noblepioneer.com', 'nomail.pw', 'nomail.xl.cx', 'nomail2me.com', 'nomorespamemails.com', 'nospam.ze.tc', 'nospam4.us', 'nospamfor.us', 'nospammail.net', 'notmailinator.com', 'nowhere.org', 'nowmymail.com', 'nurfuerspam.de', 'nus.edu.sg', 'objectmail.com', 'obobbo.com', 'odnorazovoe.ru', 'oneoffemail.com', 'onewaymail.com', 'onlatedotcom.info', 'online.ms', 'opayq.com', 'ordinaryamerican.net', 'otherinbox.com', 'ovpn.to', 'owlpic.com', 'pancakemail.com', 'pcusers.otherinbox.com', 'pjjkp.com', 'plexolan.de', 'poczta.onet.pl', 'politikerclub.de', 'poofy.org', 'pookmail.com', 'privacy.net', 'privatdemail.net', 'proxymail.eu', 'prtnx.com', 'putthisinyourspamdatabase.com', 'putthisinyourspamdatabase.com', 'qq.com', 'quickinbox.com', 'rcpt.at', 'reallymymail.com', 'realtyalerts.ca', 'recode.me', 'recursor.net', 'reliable-mail.com', 'rhyta.com', 'rmqkr.net', 'royal.net', 'rtrtr.com', 's0ny.net', 'safe-mail.net', 'safersignup.de', 'safetymail.info', 'safetypost.de', 'saynotospams.com', 'schafmail.de', 'schrott-email.de', 'secretemail.de', 'secure-mail.biz', 'senseless-entertainment.com', 'services391.com', 'sharklasers.com', 'shieldemail.com', 'shiftmail.com', 'shitmail.me', 'shitware.nl', 'shmeriously.com', 'shortmail.net', 'sibmail.com', 'sinnlos-mail.de', 'slapsfromlastnight.com', 'slaskpost.se', 'smashmail.de', 'smellfear.com', 'snakemail.com', 'sneakemail.com', 'sneakmail.de', 'snkmail.com', 'sofimail.com', 'solvemail.info', 'sogetthis.com', 'soodonims.com', 'spam4.me', 'spamail.de', 'spamarrest.com', 'spambob.net', 'spambog.ru', 'spambox.us', 'spamcannon.com', 'spamcannon.net', 'spamcon.org', 'spamcorptastic.com', 'spamcowboy.com', 'spamcowboy.net', 'spamcowboy.org', 'spamday.com', 'spamex.com', 'spamfree.eu', 'spamfree24.com', 'spamfree24.de', 'spamfree24.org', 'spamgoes.in', 'spamgourmet.com', 'spamgourmet.net', 'spamgourmet.org', 'spamherelots.com', 'spamherelots.com', 'spamhereplease.com', 'spamhereplease.com', 'spamhole.com', 'spamify.com', 'spaml.de', 'spammotel.com', 'spamobox.com', 'spamslicer.com', 'spamspot.com', 'spamthis.co.uk', 'spamtroll.net', 'speed.1s.fr', 'spoofmail.de', 'stuffmail.de', 'super-auswahl.de', 'supergreatmail.com', 'supermailer.jp', 'superrito.com', 'superstachel.de', 'suremail.info', 'talkinator.com', 'teewars.org', 'teleworm.com', 'teleworm.us', 'temp-mail.org', 'temp-mail.ru', 'tempe-mail.com', 'tempemail.co.za', 'tempemail.com', 'tempemail.net', 'tempemail.net', 'tempinbox.co.uk', 'tempinbox.com', 'tempmail.eu', 'tempmaildemo.com', 'tempmailer.com', 'tempmailer.de', 'tempomail.fr', 'temporaryemail.net', 'temporaryforwarding.com', 'temporaryinbox.com', 'temporarymailaddress.com', 'tempthe.net', 'thankyou2010.com', 'thc.st', 'thelimestones.com', 'thisisnotmyrealemail.com', 'thismail.net', 'throwawayemailaddress.com', 'tilien.com', 'tittbit.in', 'tizi.com', 'tmailinator.com', 'toomail.biz', 'topranklist.de', 'tradermail.info', 'trash-mail.at', 'trash-mail.com', 'trash-mail.de', 'trash2009.com', 'trashdevil.com', 'trashemail.de', 'trashmail.at', 'trashmail.com', 'trashmail.de', 'trashmail.me', 'trashmail.net', 'trashmail.org', 'trashymail.com', 'trialmail.de', 'trillianpro.com', 'twinmail.de', 'tyldd.com', 'uggsrock.com', 'umail.net', 'uroid.com', 'us.af', 'venompen.com', 'veryrealemail.com', 'viditag.com', 'viralplays.com', 'vpn.st', 'vsimcard.com', 'vubby.com', 'wasteland.rfc822.org', 'webemail.me', 'weg-werf-email.de', 'wegwerf-emails.de', 'wegwerfadresse.de', 'wegwerfemail.com', 'wegwerfemail.de', 'wegwerfmail.de', 'wegwerfmail.info', 'wegwerfmail.net', 'wegwerfmail.org', 'wh4f.org', 'whyspam.me', 'willhackforfood.biz', 'willselfdestruct.com', 'winemaven.info', 'wronghead.com', 'www.e4ward.com', 'www.mailinator.com', 'wwwnew.eu', 'x.ip6.li', 'xagloo.com', 'xemaps.com', 'xents.com', 'xmaily.com', 'xoxy.net', 'yep.it', 'yogamaven.com', 'yopmail.com', 'yopmail.fr', 'yopmail.net', 'yourdomain.com', 'yuurok.com', 'z1p.biz', 'za.com', 'zehnminuten.de', 'zehnminutenmail.de', 'zippymail.info', 'zoemail.net', 'zomg.info', '0hio0ak.com', '10mail.org', '10mail.tk', '127.life', '1mail.x24hr.com', '23.8.dnsabr.com', '32core.live', '34nm.com', '4dentalsolutions.com', '816qs.com', '888.dns-cloud.net', '8.dnsabr.com', '99email.xyz', 'actitz.site', 'adaov.com', 'adult-work.info', 'aenikaufa.com', 'ahem.email', 'ahem-email.com', 'aintcheap.com', 'altmails.com', 'amail4.me', 'amail.club', 'anomail.club', 'anonymized.org', 'anywhere.pw', 'appzily.com', 'asia.dnsabr.com', 'badlion.co.uk', 'bambase.com', 'bambotv.com', 'bareed.ws', 'barretodrums.com', 'b.cr.cloudns.asia', 'bd.dns-cloud.net', 'bestofdedicated.com', 'besttempmail.com', 'billseo.com', 'biyac.com', 'blackturtle.xyz', 'budaya-tionghoa.com', 'budayationghoa.com', 'burgas.vip', 'buybacklink.biz', 'buy-blog.com', 'bylup.com', 'cars2.club', 'chapedia.net', 'chapedia.org', 'chasefreedomactivate.com', 'chiet.ru', 'cloud-mail.top', 'cmail.club', 'contactwithme.com', 'coolmailcool.com', 'corona.is.bullsht.dedyn.io', 'cpmail.life', 'cr.cloudns.asia', 'crepeau12.com', 'cudimex.com', 'cuoly.com', 'cxmyal.com', 'dencxvo.com', 'deps.cf', 'desoz.com', 'dhivehinews.site', 'diptoes.com', 'disbox.net', 'disbox.org', 'discard.email', 'discardmail.com', 'discardmail.computer', 'discardmail.de', 'discardmail.live', 'discardmail.ninja', 'disdraplo.com', 'dispomail.xyz', 'disposable-email.ml', 'disposable.ml', 'doc-mail.net', 'dristypat.com', 'dropmail.me', 'duck2.club', 'dvd.dnsabr.com', 'dvd.dns-cloud.net', 'dznf.net', 'easy-trash-mail.com', 'emailisvalid.com', 'email-jetable.biz.st', 'email-jetable.co.tv', 'email-jetable.cz.cc', 'email-jetable.fr', 'email-temporaire.cz.cc', 'emlhub.com', 'emlpro.com', 'emltmp.com', 'eoopy.com', 'eu.dnsabr.com', 'eu.dns-cloud.net', 'everybodyweb.com', 'fakemail.top', 'fexbox.org', 'fexbox.ru', 'fexpost.com', 'finemail.org', 'fineoak.org', 'firemailbox.club', 'firste.ml', 'fouadps.cf', 'freeallapp.com', 'freeml.net', 'freundin.ru', 'from.onmypc.info', 'fshare.ootech.vn', 'geneseeit.com', 'getnada.com', 'gettempmail.com', 'greencafe24.com', 'gripam.com', 'gu5t.com', 'halumail.com', 'happy-new-year.top', 'harakirimail.se', 'haribu.net', 'hellomail.tech', 'heroku.42web.io', 'hide.biz.st', 'hidemyass.fun', 'historictheology.com', 'hourly.site', 'hubbu.online', 'iamhere.store', 'ianz.pro', 'icenhl.com', 'igosad.tech', 'incognitomail.org', 'inpwa.com', 'intopwa.com', 'intopwa.net', 'intopwa.org', 'jetable.co.cc', 'jetable.cz.cc', 'just4fun.me', 'k377.me', 'kaaaxcreators.tk', 'kentol.buzz', 'ketoblazepro.com', 'kittenemail.com', 'kittenemail.xyz', 'knol-power.nl', 'kost.party', 'kuontil.buzz', 'lackmail.ru', 'lajoska.pe.hu', 'laste.ml', 'lazyinbox.com', 'logicstreak.com', 'lsh.my.id', 'luxusmail.cf', 'luxusmail.ga', 'luxusmail.gq', 'luxusmail.ml', 'luxusmail.my.id', 'luxusmail.tk', 'maa.567map.xyz', 'mac-24.com', 'mail7.io', 'mail.a1.wtf', 'mail.ahem.email', 'mailbox.in.ua', 'mailboxvip.com', 'mailgano.com', 'mailgen.biz', 'mailgen.club', 'mailgen.fun', 'mailgen.info', 'mailgen.io', 'mailgen.pro', 'mailgen.pw', 'mailgen.xyz', 'mailglobe.club', 'mailglobe.org', 'mailg.ml', 'mailgun.org', 'mailhazard.com', 'mailhazard.us', 'mailhz.me', 'mail.igosad.me', 'mail-jetable.co.tv', 'mail-jetable.cz.cc', 'mail.kaaaxcreators.tk', 'mail.lgbtiqa.xyz', 'mail.mrgamin.ml', 'mailpoof.com', 'mailsac.com', 'mails.v2-ray.net', 'mailtemp.net', 'mail-temporaire.com', 'mailtemporaire.com', 'mail-temporaire.cz.cc', 'mailtemporaire.fr', 'mailto.plus', 'markmail.site', 'marmaryta.club', 'marmaryta.com', 'marmaryta.email', 'marmaryta.space', 'matapad.com', 'm.cloudns.cl', 'm.discardmail.org', 'meadowutilities.com', 'meantinc.com', 'media.motornation.buzz', 'mentonit.net', 'mepost.pw', 'mexcool.com', 'mfsa.ru', 'mhzayt.online', 'mm.8.dnsabr.com', 'moakt.cc', 'moakt.co', 'moakt.ws', 'mobj.site', 'mowgli.jungleheart.com', 'mrdeeps.ml', 'mrgamin.cf', 'mrgamin.gq', 'mrgamin.ml', 'msft.cloudns.asia', 'myinternet.site', 'mymail.infos.st', 'mysukam.com', 'mywrld.top', 'nanozone.net', 'nccedu.media', 'nccedu.team', 'ndeooo.club', 'ndeooo.com', 'ndeooo.xyz', 'netmail.tk', 'nicoric.com', 'noclickemail.com', 'nospamme.rs', 'notmyemail.tech', 'noway.pw', 'now.mefound.com', 'nvc-e.com', 'omailer.xyz', 'ondemandemail.top', 'oneideas.xyz', 'onlinemaster.xyz', 'opencube.xyz', 'ottappmail.com', 'outlook-mails.site', 'padpub.co.cc', 'padpub.co.tv', 'panarabanesthesia2021.live', 'pecinan.com', 'pecinan.net', 'pecinan.org', 'pflege-schoene-haut.de', 'plexvenet.com', 'pokemail.net', 'polostar.me', 'postheo.de', 'powerencry.com', 'ppc-e.com', 'privacy-mail.top', 'pw.8.dnsabr.com', 'pw.epac.to', 'qrtise.com', 'quickbuy4u.online', 'randomail.net', 'rcedu.team', 'revampall.com', 'robot-mail.com', 'rover.info', 'rsvpee.com', 'safeemail.xyz', 'savageattitude.com', 'sexy.camdvr.org', 'shit.dnsabr.com', 'shit.dns-cloud.net', 'sinkafbet.net', 'skug.net', 'slowimo.com', 'smack.email', 'sociallifes.club', 'sokuyo.xyz', 'solpatu.space', 'spambog.com', 'spambog.de', 'spam.destroyer.email', 'spamsandwich.com', 'speedmail.ze.cx', 'squizzy.net', 'sroff.com', 'ssl.tls.cloudns.asia', 'stepoly.com', 'stevenledford.com', 'supere.ml', 'sweetxxx.de', 't20mail.com', 'tamchiasao.com', 'tech-guru.site', 'techwizardent.me', 'tempemail.info', 'tempes.gq', 'tempmail.digital', 'tempmail.wizardmail.tech', 'temporary-mail.net', 'tempr.email', 'tempsky.com', 'tempsky.top', 'tempxmail.info', 'the23app.com', 'thejoker5.com', 'throwam.com', 'tls.cloudns.asia', 'tmails.net', 'tmail.ws', 'tmpbox.net', 'tmpmail.net', 'tmpmail.org', 'tmpnator.live', 'tokyoto.site', 'tovinit.com', 'trap-mail.de', 'trashmail.es', 'trashmail.win', 'trashmail.ws', 'traz.cafe', 'trbvm.com', 'truthfinderlogin.com', 'ttlrlie.com', 'tuneme.online', 'twitter-sign-in.cf', 't.woeishyang.com', 'typery.com', 'vintomaper.com', 'vipmailonly.info', 'viralchoose.com', 'virtualdepot.store', 'virtual-generations.com', 'viruschecks.co', 'vvaa1.com', 'wc.pisskegel.de', 'wearsn.com', 'wellsfargocomcardholders.com', 'wimsg.com', 'wmail.club', 'wmcasinoauto.com', 'xxxxx.cyou', 'yahoo-emails.online', 'yaud.net', 'yepmail.app', 'yepmail.cc', 'yepmail.club', 'yepmail.co', 'yepmail.id', 'yepmail.in', 'yepmail.to', 'yepmail.us', 'yepmail.ws', 'yomail.info', 'you.has.dating', 'yx.dns-cloud.net', 'zadder.xyz', 'temp-mail.io', 'express.net.ua', 'mycard.net.ua', 'card.zp.ua', 'email.zp.ua', 'infocom.zp.ua', 'mail.zp.ua', 'zebins.com', 'zebins.eu', 'zeroe.ml', 'zwoho.com']
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
