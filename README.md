<<<<<<< HEAD
# Odoo.sh reposistory for Form project

This reposistory contains the modules required to run Form project on Odoo.sh.

It also contains odoo.conf file that helps to run a local instance using the submodules defined in the repository.

## #How to use this repo in a local instance?

The configuration of the file assumes that the folder structure for the project is the following.

```shell-script
~/Projects/odoo-sh/<reposistory-name>
~/Projects/14.0/odoo
~/Projects/14.0/enterprise
```

You can run the following command when your working directory is the reposistory.

```shell-script
cd ~/Projects/odoo-sh/<reposistory-name>
../../14.0/odoo/odoo-bin -c ./odoo.conf
```

You can also define the following function in your ~/.zshrc or ~/.bash_profile file

```shell-script
function odoo-sh() {
    # If there is no argument define the default value for this variable
    local database=${1:-test140}
    local repo=${2}
    # Validate if the first argument is not defined, if it's not defined it will not call the shift
    if [ ! -z "$1" ]
    then
        shift 1 # Remove the first argument
    fi
    shift 1
    cd ~/Projects/odoo-sh/"$repo"
    python3 ~/Projects/14.0/odoo/odoo-bin -c ~/Projects/odoo-sh/"$repo"/odoo.conf -d "$database" --db-filter="$database" "$@"
}
```

After you restart the console or `source ~/.zshrc` or `source ~/.bash_profile` you can run a odoo instance using the following command

```shell-script
odoo-sh <database-name> <reposistory-name>
```

Where:
- **database-name:** the name of the database that will be used.
- **repository-name:** must be the the name of the Odoo.sh reposistory name.

You can also pass more parameters used to run odoo for example:

```shell-script
odoo-sh <database-name> <reposistory-name> -i l10n_mx --load-language=es_MX
```
=======
# Form repository

>>>>>>> 46c6ce471c201ae7dbb5178469f57aec67619278
