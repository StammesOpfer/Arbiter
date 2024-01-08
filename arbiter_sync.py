#!/usr/bin/env python3
import ldap3
import configparser
import argparse
import getpass

# Import config from ini
config = configparser.ConfigParser()
config.read('arbiter_config.ini')

# Parse cli args if present
parser = argparse.ArgumentParser(description="FreeIPA Group Sync to support vCenter")
parser.add_argument('-p', '--password', action='store_true', help="Interactive password entry")
parser.add_argument('-f', '--fix', action='store_true', help="Add missing group attributes")
args = parser.parse_args()

# Assign config values to variables
ldaps_server = config.get('LDAP', 'server')
ldaps_user = config.get('LDAP', 'user')
base_dn = config.get('LDAP', 'groupdn')
group_filter = config.get('LDAP', 'groupfilter')

# Prompt the user for a password if -p is provided, otherwise read it from the config file
if args.fix:
    ldaps_user = f'uid=admin,{ldaps_user.split(",", 1)[1]}'
    print(f'User = {ldaps_user}')
    ldaps_password = getpass.getpass("Enter the Admin LDAP password: ")
elif args.password:
    ldaps_password = getpass.getpass("Enter your LDAP password: ")
else:
    ldaps_password = config.get('LDAP', 'password')

# Create an LDAP connection with LDAPS
connection = ldap3.Connection(ldaps_server, ldaps_user, ldaps_password, auto_bind=True)

print()
# Check the connection to the server
if not connection.bind():
    print("LDAP bind failed")
    exit()

if args.fix:
    connection.search(base_dn, group_filter, attributes=['objectClass'])
    for entry in connection.entries:
        if 'groupsofuniquenames' not in entry.objectClass.values:
            connection.modify(entry.entry_dn, {'objectClass': [(ldap3.MODIFY_ADD, 'groupOfUniqueNames')]})
        group_dn = entry.entry_dn


# Search for groups that match the filter
connection.search(base_dn, group_filter, attributes=['member', 'uniqueMember'])

# Iterate through the group search results and update individual uniqueMembers
for entry in connection.entries:
    group_dn = entry.entry_dn
    current_unique_members = set(entry.uniqueMember.values)
    current_members = set(entry.member.values)

    # Calculate the differences between members and uniqueMembers
    members_diff = current_members - current_unique_members
    unique_members_diff = current_unique_members - current_members

    # If there is a difference modify uniqueMembers to match memebers
    if members_diff or unique_members_diff:
        group_cn = group_dn.split(',')[0].split('=')[1] # Extract CN from DN
        print(f"\nChanges made to group \033[38;5;215m{group_cn}\033[0m:")
        # If member needs to be added
        if members_diff:
            connection.modify(group_dn, {'uniqueMember': [(ldap3.MODIFY_ADD, list(members_diff))]})
            for member in members_diff:
                print(f"\033[38;5;215m{member.split(',')[0].split('=')[1]}\033[0m \033[32madded\033[0m to: \033[38;5;215muniqueMembers\033[0m")
        
        # If member needs to be removed
        if unique_members_diff:
            connection.modify(group_dn, {'uniqueMember': [(ldap3.MODIFY_DELETE, list(unique_members_diff))]})
            for member in unique_members_diff:
                print(f"\033[38;5;215m{member.split(',')[0].split('=')[1]}\033[0m \033[31mremoved\033[0m from: \033[38;5;215muniqueMembers\033[0m")

        if connection.result['result'] == 0:
            print(f"\nSuccessful synchronization of group: \033[38;5;215m{group_cn}\033[0m.\n")
        else:
            print(f"Synchronization for group: {group_cn} \033[31mfailed\033[0m. Error:", connection.result['description'])
    # If lists match and nothing needs to occur
    else:
        print(f"No updates detected for group: \033[38;5;215m{group_dn.split(',')[0].split('=')[1]}\033[0m.")
print()
# Unbind and close the LDAP connection
connection.unbind()
