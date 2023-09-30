# Arbiter
## A way to make VMware vCenter and FreeIPA work together. <br> Schema updater and group member syncing.
Built on vSphere 7 and FreeIPA 4.10 (Should support at minimum vCenter 6.5 - 8.0)
Arbiter creates all the schema that vCenter expects (groupOfUniqueNames and uniqueMember) and permissions to view those new attributes. It also populates the attributes and syncs the FreeIPA "member" attribute to the "uniqueMember" attribute that vCenter reads and uses. What this means is that you FreeIPA groups now work in vCenter.

## Instructions


### First time configuration
Run arbiter_setup.sh on the FreeIPA server which will add the required attributes, privileges, permissions, roles, and user. All are labeled "Arbiter-Sync'' for easy identification.
```
chmod u+x arbiter_setup.sh
./arbiter_setup.sh
```
### Edit Config
Update the `arbiter_config.ini` file to match your environment (FreeIPA url and "dc" values). Password is optional if you are not going to schedule the script.
The filter option reduces the updates that must be accomplished by only running against certain groups. This is likely only needed in large environments.

### Syncing users
Ensure the ldap3 module is available
```
pip3 install ldap3
```
Run
```
python3 arbitor_sync.py
```
You can use the `-p` flag to be prompted for the password rather than storing it in the config file.

If you created your groups before running `arbiter_setup.sh`, run `arbiter_sync.py --fix` once to add proper attributes to existing groups (may also be impacted by changing filters).

Sync can be run at regular intervals by scheduling it via cron.