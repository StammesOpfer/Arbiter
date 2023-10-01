#!/bin/bash
# Cache Kerberos ticket
echo '';echo 'IPA Admin access to accomplish required setup tasks'
kinit admin
# Create a user for syncing.
echo '';echo '';echo 'Creating Arbiter-Sync-User. This password needs to be entered into the arbiter_config.ini or it can be used for interactive execution.'
ipa user-add Arbiter-Sync-User --password --first=Arbiter --last=Sync
ipa group-remove-member ipausers --users=Arbiter-Sync-User
# Add groupOfUniqueNames to support the uniqueMember attribute vCenter looks for.
ipa config-mod --addattr=ipagroupobjectclasses=groupofuniquenames
# Add uniqueMember to values that can be read by vCenter.
ipa permission-mod "System: Read Groups" --includedattrs=uniquemember
# Add privilege to modify only the uniqieMember attribute so the script can sync the to the normal member attribute.
ipa permission-add Arbiter-Sync-Permission --bindtype=permission --right=write --type=group --attr=uniquemember
# Create a privilege with the above permission assigned.
ipa privilege-add Arbiter-Sync-Privilege
ipa privilege-add-permission Arbiter-Sync-Privilege --permissions=Arbiter-Sync-Permission
# Create a role with the above priviledge and user assigned.
ipa role-add Arbiter-Sync-Role
ipa role-add-privilege Arbiter-Sync-Role  --privileges=Arbiter-Sync-Privilege
ipa role-add-member Arbiter-Sync-Role --users=Arbiter-Sync-User