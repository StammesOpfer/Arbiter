#!/bin/bash
# Cache Kerberos ticket
kinit admin
# Add groupOfUniqueNames to support the uniqueMember attribute vCenter looks for.
ipa config-mod --addattr=ipagroupobjectclasses=groupofuniquenames
# Add uniqueMember to values that can be read by vCenter.
ipa permission-mod "System: Read Groups" --includedattrs=uniquemember
# Add priviledge to modify only the uniqieMember attribute so the script can sync the to the normal member attribute.
ipa permission-add Arbiter-Sync-Permission --bindtype=permission --right=write --type=group --attr=uniquemember
# Discover the base domain for the next step.
domain=$(ipa permission-show Arbiter-Sync-Permission | grep Subtree | awk -F dc '{for (i=2; i<NF; i++) printf "dc"$i; print "dc"$NF}')
# Create a privilege with the above permission assigned.
ipa privilege-add Arbiter-Sync-Privilege --setattr=memberof=cn=Arbiter-Sync-Permission,cn=permissions,cn=pbac,$domain
# Create a user for syncing.
echo ''; echo 'This password needs to be entered into the arbiter_config.ini or it can be used for interactive execution'
ipa user-add Arbiter-Sync-User --password --first=Arbiter --last=Sync
# Create a role with the above priviledge assigned.
ipa role-add Arbiter-Sync-Role --setattr=memberof=cn=Arbiter-Sync-Privilege,cn=privileges,cn=pbac,$domain --setattr=member=uid=Arbiter-Sync-User,cn=users,cn=accounts,$domain
