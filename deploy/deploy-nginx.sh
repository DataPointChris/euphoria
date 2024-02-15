#!/usr/bin/env bash

######################################################################
# Deploy to Environment
######################################################################

# Fail script on command fail
set -e


SCRIPT_NAME="$0"

usage() {
    local message
    message=$(cat <<-EOF
        $(green "$(print_section "Deploy Supervisor and NGINX Config Files")")

        $(green "Usage:")
        Run as $SCRIPT_NAME {dev, test, prod}

        $(green "Example:")
        $SCRIPT_NAME dev

        $(green "Help:")
        $SCRIPT_NAME --help
EOF
)
    echo "$message"
}


help() {
    local message
    message=$(cat <<-EOF
        $(usage)

        $(green "Script Actions:")
        Copy: NGINX config file
        Copy: NGINX sites-available config file(s)
        Symlink: NGINX sites-enabled config file(s)

        Copy: Supervisor config file
        Copy: Supervisor api config file
        Copy: Supervisor app config file
        Create: Supervisor api log files
        Create: Supervisor app log files

        $(green "Dependencies")
        nginx
        supervisor
EOF
)
    echo "$message"
}


#-------------------- SCRIPT PRE-PROCESSING --------------------#
# Get project name from current dir
PROJECT=$(basename "$PWD")

# -- Check for arguments -- #
# NOTE: No exit codes inside the functions so they can be more generic

# 1. If no arguments: show usage, no error
if [[ -z "$1" ]]; then
    usage
    exit 0;

# 2. Check for particular flags
elif [[ "$1" = "--help" ]]; then
    shift
    help "$@"
    exit 0;
fi

# 3. Assign variables
# Get environment flag
ENVIRONMENT=$1
case $ENVIRONMENT in
    dev) OS_PREFIX="/usr/local" ;;
    test) OS_PREFIX="" ;;
    prod) OS_PREFIX="" ;;
    *) echo_error "Unsupported environment flag: $ENVIRONMENT"
       usage
       exit 1 ;;
esac

#-------------------- MAIN SCRIPT --------------------#

# Project File Locations
ENV_DEPLOY_DIR="deploy/$ENVIRONMENT"
NGINX_DEPLOY_DIR="$ENV_DEPLOY_DIR/nginx"
SUPERVISOR_DEPLOY_DIR="$ENV_DEPLOY_DIR/supervisor"

# Config Locations
ETC_DIR="$OS_PREFIX/etc"

NGINX_DIR="$ETC_DIR/nginx"
NGINX_SITES_AVAILABLE="$NGINX_DIR/sites-available"
NGINX_SITES_ENABLED="$NGINX_DIR/sites-enabled"

SUPERVISOR_DIR="$ETC_DIR/supervisor"
SUPERVISOR_CONFIG_DIR="$SUPERVISOR_DIR/conf.d"
SUPERVISOR_LOG_DIR="$OS_PREFIX/var/log/supervisor"


print_title "Deploying $PROJECT project in $ENVIRONMENT environment"


# ---------- NGINX ----------- #
print_section "NGINX"

# Directories
sudo mkdir -p $NGINX_SITES_AVAILABLE
sudo mkdir -p $NGINX_SITES_ENABLED

notify_create $NGINX_SITES_AVAILABLE
notify_create $NGINX_SITES_ENABLED

# Configuration
sudo cp "$NGINX_DEPLOY_DIR/nginx.conf" "$NGINX_DIR/nginx.conf"
sudo cp "$NGINX_DEPLOY_DIR/api.conf" "$NGINX_SITES_AVAILABLE/$PROJECT-api.conf"
sudo cp "$NGINX_DEPLOY_DIR/app.conf" "$NGINX_SITES_AVAILABLE/$PROJECT-app.conf"

notify_copy "$NGINX_DEPLOY_DIR/nginx.conf" "$NGINX_DIR/nginx.conf"
notify_copy "$NGINX_DEPLOY_DIR/api.conf" "$NGINX_SITES_AVAILABLE/$PROJECT-api.conf"
notify_copy "$NGINX_DEPLOY_DIR/app.conf" "$NGINX_SITES_AVAILABLE/$PROJECT-app.conf"

# Symlink from sites-available to sites-enabled
sudo ln -sf "$NGINX_SITES_AVAILABLE/$PROJECT-api.conf" "$NGINX_SITES_ENABLED/$PROJECT-api.conf"
sudo ln -sf "$NGINX_SITES_AVAILABLE/$PROJECT-app.conf" "$NGINX_SITES_ENABLED/$PROJECT-app.conf"

notify_symlink "$NGINX_SITES_AVAILABLE/$PROJECT-api.conf" "$NGINX_SITES_ENABLED/$PROJECT-api.conf"
notify_symlink "$NGINX_SITES_AVAILABLE/$PROJECT-app.conf" "$NGINX_SITES_ENABLED/$PROJECT-app.conf"
echo


# ---------- Supervisor ---------- #
print_section "SUPERVISOR"
# Note: Make sure log direcitories match entries in `supervisord.conf`

# Directories
sudo mkdir -p $SUPERVISOR_DIR
sudo mkdir -p $SUPERVISOR_CONFIG_DIR
sudo mkdir -p $SUPERVISOR_LOG_DIR

notify_create $SUPERVISOR_DIR
notify_create $SUPERVISOR_CONFIG_DIR
notify_create $SUPERVISOR_LOG_DIR

# Configs
sudo cp "$SUPERVISOR_DEPLOY_DIR/supervisord.conf" "$SUPERVISOR_DIR/supervisord.conf"
sudo cp "$SUPERVISOR_DEPLOY_DIR/app.conf" "$SUPERVISOR_CONFIG_DIR/$PROJECT-app.conf"
sudo cp "$SUPERVISOR_DEPLOY_DIR"/api.conf "$SUPERVISOR_CONFIG_DIR/$PROJECT-api.conf"

notify_copy "$SUPERVISOR_DEPLOY_DIR/supervisord.conf" "$SUPERVISOR_DIR/supervisord.conf"
notify_copy "$SUPERVISOR_DEPLOY_DIR/app.conf" "$SUPERVISOR_CONFIG_DIR/$PROJECT-app.conf"
notify_copy "$SUPERVISOR_DEPLOY_DIR/api.conf" "$SUPERVISOR_CONFIG_DIR/$PROJECT-api.conf"

# Logs
sudo touch "$SUPERVISOR_LOG_DIR/supervisord.log"
sudo touch "$SUPERVISOR_LOG_DIR/$PROJECT-app.log"
sudo touch "$SUPERVISOR_LOG_DIR/$PROJECT-api.log"

notify_create "$SUPERVISOR_LOG_DIR/supervisord.log"
notify_create "$SUPERVISOR_LOG_DIR/$PROJECT-app.log"
notify_create "$SUPERVISOR_LOG_DIR/$PROJECT-api.log"
echo ""


# ---------- Set owner on MacOS in dev ---------- #
if [[ $ENVIRONMENT = "dev" ]]; then
    print_section "PERMISSIONS"
    sudo chown -R "$USER" $NGINX_DIR
    sudo chown -R "$USER" $SUPERVISOR_DIR
    sudo chown -R "$USER" $SUPERVISOR_LOG_DIR
    echo "Change owner of $(green "$NGINX_DIR/") to user: $(blue "$USER")"
    echo "Change owner of $(green "$SUPERVISOR_DIR/") to user: $(blue "$USER")"
    echo "Change owner of $(green "$SUPERVISOR_LOG_DIR/") to user: $(blue "$USER")"
    echo
fi


# ---------- Apache ---------- #
# Change permissions for www folder
# sudo chown -R $USER:www-data /var/www
# sudo find /var/www -type d -exec chmod 2750 {} \+
# sudo find /var/www -type f -exec chmod 640 {} \+



# ---------- Success ---------- #
print_title "All files copied"
echo
blue "Remember to restart nginx and supervisor:"
echo "sudo supervisorctl reload"
echo "sudo nginx -s reload"
echo