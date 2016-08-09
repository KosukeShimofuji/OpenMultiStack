# OpenMultiStack

OpenMultiStackは複数のOpenStack Providerをまたがってcomptue nodeの作成や破棄といった操作と管理を一元化するために作成しました。OpenMultiStackには次のような機能が実装されています。

 * OpenStackアカウントの集約
 * WebインターフェイスからOpenStack Providerのアカウント登録できる
 * Webインターフェイスからインスタンス情報の一覧を見ることができる
 * いずれかのOpenStack Providerにメンテナンスや不具合があったとしても他のOpenStack Providerを使って可能な限り確実にインスタンスを立ち上げるように努力する
 * クライアントとの通信はRESTful APIで行う

# 検証環境のDEPLOY

 * 検証環境の作成

```
$ cd OpenMultiStack/ansible
$ vagrant up
$ ansible-playbook -i development site.yml
```

 * デプロイ用の構成を作成

```
$ sudo mkdir -p /var/www/OpenMultiStack/
$ cd ~/
$ git clone git@github.com:KosukeShimofuji/OpenMultiStack.git
$ cd OpenMultiStack
```

 * pyenvのインストール

```
$ git clone https://github.com/yyuu/pyenv.git ~/.pyenv
$ cat ~/.bash_profile
export PYENV_ROOT=/home/kosuke/.pyenv
export PATH=$PYENV_ROOT/bin:$PATH
eval "$(pyenv init -)"
```

 * Python 3.5.1のインストール

```
$ CFLAGS="-fPIC" pyenv install 3.5.1
$ pyenv global 3.5.1
```

 * Pythonモジュールのインストール

```
$ pip install --upgrade pip
$ pip install django
$ pip install psycopg2 # djangoからpostgresqlを操作するために必要
$ pip install djangorestframework
$ pip install django-filter 
$ pip install python-openstackclient
$ pip install python-neutronclient
$ pip install celery
$ pip install django-celery
$ pip install sqlalchemy
```

 * モデルのマイグレート

```
$ cd OpenMultiStack/django_project/
$ python manage.py makemigrations open_multi_stack
$ python manage.py migrate
```

 * django test serverの起動

```
$ python manage.py runserver 0.0.0.0:8000
```

 * celery serverの起動

```
$ celery -A django_project worker -l info -c 1
```

 * 管理ユーザの作成

```
$ python manage.py createsuperuser
Username (leave blank to use 'kosuke'): kosuke
Email address: kosuke.shimofuji@gmail.com
Password:
Password (again):
Superuser created successfully.
```

 * mod_wsgiのインストール

```
$ sudo apt-get install apache2-dev
$ wget https://pypi.python.org/packages/c3/4e/f9bd165369642344e8fdbe78c7e820143f73d3beabfba71365f27ee5e4d3/mod_wsgi-4.5.3.tar.gz
$ tar zxvf mod_wsgi-4.5.3.tar.gz
$ cd mod_wsgi-4.5.3
$ ./configure --with-python=/home/kosuke/.pyenv/versions/3.5.1/bin/python
$ make
$ sudo make install
$ sudo sh -c 'cat > /etc/apache2/mods-available/wsgi.load'
LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi.so
CTRL+C
$ sudo a2enmod wsgi
```

 * Apache用の設定ファイルを用意する。 

/etc/apache2/sites-available/open_multi_stack.conf

```
WSGISocketPrefix /var/run/wsgi

<VirtualHost *:80>

  ServerName   oms.test

  WSGIScriptReloading On
  WSGIDaemonProcess  oms.test python-path=/home/kosuke/OpenMultiStack/django_project:/home/kosuke/OpenMultiStack/.pyenv/versions/3.5.1/lib/python3.5/site-packages python-home=/home/kosuke/.pyenv/versions/3.5.1 user=www-data group=www-data processes=2 threads=25
  WSGIProcessGroup oms.test
  WSGIScriptAlias    / /home/kosuke/OpenMultiStack/django_project/django_project/wsgi.py

  Alias /static/ /var/www/OpenMultiStack/static/

  <Directory /var/www/OpenMultiStack/static>
  Order deny,allow
  Allow from all
  </Directory>

  <Directory "/home/kosuke/OpenMultiStack/django_project/django_project">
  <Files wsgi.py>
        Require all granted
  </Files>
  </Directory>

  ErrorLog /var/log/apache2/django-error.log
  CustomLog /var/log/apache2/django-access.log combined

</VirtualHost>
```

 * 静的ファイルをを集める。

```
# python manage.py collectstatic
```

 * /etc/init.d/celelyd

```

#!/bin/sh -e
# ============================================
#  celeryd - Starts the Celery worker daemon.
# ============================================
#
# :Usage: /etc/init.d/celeryd {start|stop|force-reload|restart|try-restart|status}
# :Configuration file: /etc/default/celeryd
#
# See http://docs.celeryproject.org/en/latest/tutorials/daemonizing.html#generic-init-scripts


### BEGIN INIT INFO
# Provides:          celeryd
# Required-Start:    $network $local_fs $remote_fs
# Required-Stop:     $network $local_fs $remote_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: celery task worker daemon
### END INIT INFO
#
#
# To implement separate init scripts, copy this script and give it a different
# name:
# I.e., if my new application, "little-worker" needs an init, I
# should just use:
#
#   cp /etc/init.d/celeryd /etc/init.d/little-worker
#
# You can then configure this by manipulating /etc/default/little-worker.
#
VERSION=10.1
echo "celery init v${VERSION}."
if [ $(id -u) -ne 0 ]; then
    echo "Error: This program can only be used by the root user."
    echo "       Unprivileged users must use the 'celery multi' utility, "
    echo "       or 'celery worker --detach'."
    exit 1
fi

origin_is_runlevel_dir () {
    set +e
    dirname $0 | grep -q "/etc/rc.\.d"
    echo $?
}

# Can be a runlevel symlink (e.g. S02celeryd)
if [ $(origin_is_runlevel_dir) -eq 0 ]; then
    SCRIPT_FILE=$(readlink "$0")
else
    SCRIPT_FILE="$0"
fi
SCRIPT_NAME="$(basename "$SCRIPT_FILE")"

DEFAULT_USER="celery"
DEFAULT_PID_FILE="/var/run/celery/%n.pid"
DEFAULT_LOG_FILE="/var/log/celery/%n.log"
DEFAULT_LOG_LEVEL="INFO"
DEFAULT_NODES="celery"
DEFAULT_CELERYD="-m celery worker --detach"

CELERY_DEFAULTS=${CELERY_DEFAULTS:-"/etc/default/${SCRIPT_NAME}"}

# Make sure executable configuration script is owned by root
_config_sanity() {
    local path="$1"
    local owner=$(ls -ld "$path" | awk '{print $3}')
    local iwgrp=$(ls -ld "$path" | cut -b 6)
    local iwoth=$(ls -ld "$path" | cut -b 9)

    if [ "$(id -u $owner)" != "0" ]; then
        echo "Error: Config script '$path' must be owned by root!"
        echo
        echo "Resolution:"
        echo "Review the file carefully and make sure it has not been "
        echo "modified with mailicious intent.  When sure the "
        echo "script is safe to execute with superuser privileges "
        echo "you can change ownership of the script:"
        echo "    $ sudo chown root '$path'"
        exit 1
    fi

    if [ "$iwoth" != "-" ]; then  # S_IWOTH
        echo "Error: Config script '$path' cannot be writable by others!"
        echo
        echo "Resolution:"
        echo "Review the file carefully and make sure it has not been "
        echo "modified with malicious intent.  When sure the "
        echo "script is safe to execute with superuser privileges "
        echo "you can change the scripts permissions:"
        echo "    $ sudo chmod 640 '$path'"
        exit 1
    fi
    if [ "$iwgrp" != "-" ]; then  # S_IWGRP
        echo "Error: Config script '$path' cannot be writable by group!"
        echo
        echo "Resolution:"
        echo "Review the file carefully and make sure it has not been "
        echo "modified with malicious intent.  When sure the "
        echo "script is safe to execute with superuser privileges "
        echo "you can change the scripts permissions:"
        echo "    $ sudo chmod 640 '$path'"
        exit 1
    fi
}

if [ -f "$CELERY_DEFAULTS" ]; then
    _config_sanity "$CELERY_DEFAULTS"
    echo "Using config script: $CELERY_DEFAULTS"
    . "$CELERY_DEFAULTS"
fi

# Sets --app argument for CELERY_BIN
CELERY_APP_ARG=""
if [ ! -z "$CELERY_APP" ]; then
    CELERY_APP_ARG="--app=$CELERY_APP"
fi

CELERYD_USER=${CELERYD_USER:-$DEFAULT_USER}

# Set CELERY_CREATE_DIRS to always create log/pid dirs.
CELERY_CREATE_DIRS=${CELERY_CREATE_DIRS:-0}
CELERY_CREATE_RUNDIR=$CELERY_CREATE_DIRS
CELERY_CREATE_LOGDIR=$CELERY_CREATE_DIRS
if [ -z "$CELERYD_PID_FILE" ]; then
    CELERYD_PID_FILE="$DEFAULT_PID_FILE"
    CELERY_CREATE_RUNDIR=1
fi
if [ -z "$CELERYD_LOG_FILE" ]; then
    CELERYD_LOG_FILE="$DEFAULT_LOG_FILE"
    CELERY_CREATE_LOGDIR=1
fi

CELERYD_LOG_LEVEL=${CELERYD_LOG_LEVEL:-${CELERYD_LOGLEVEL:-$DEFAULT_LOG_LEVEL}}
CELERY_BIN=${CELERY_BIN:-"celery"}
CELERYD_MULTI=${CELERYD_MULTI:-"$CELERY_BIN multi"}
CELERYD_NODES=${CELERYD_NODES:-$DEFAULT_NODES}

export CELERY_LOADER

if [ -n "$2" ]; then
    CELERYD_OPTS="$CELERYD_OPTS $2"
fi

CELERYD_LOG_DIR=`dirname $CELERYD_LOG_FILE`
CELERYD_PID_DIR=`dirname $CELERYD_PID_FILE`

# Extra start-stop-daemon options, like user/group.
if [ -n "$CELERYD_CHDIR" ]; then
    DAEMON_OPTS="$DAEMON_OPTS --workdir=$CELERYD_CHDIR"
fi


check_dev_null() {
    if [ ! -c /dev/null ]; then
        echo "/dev/null is not a character device!"
        exit 75  # EX_TEMPFAIL
    fi
}


maybe_die() {
    if [ $? -ne 0 ]; then
        echo "Exiting: $* (errno $?)"
        exit 77  # EX_NOPERM
    fi
}

create_default_dir() {
    if [ ! -d "$1" ]; then
        echo "- Creating default directory: '$1'"
        mkdir -p "$1"
        maybe_die "Couldn't create directory $1"
        echo "- Changing permissions of '$1' to 02755"
        chmod 02755 "$1"
        maybe_die "Couldn't change permissions for $1"
        if [ -n "$CELERYD_USER" ]; then
            echo "- Changing owner of '$1' to '$CELERYD_USER'"
            chown "$CELERYD_USER" "$1"
            maybe_die "Couldn't change owner of $1"
        fi
        if [ -n "$CELERYD_GROUP" ]; then
            echo "- Changing group of '$1' to '$CELERYD_GROUP'"
            chgrp "$CELERYD_GROUP" "$1"
            maybe_die "Couldn't change group of $1"
        fi
    fi
}


check_paths() {
    if [ $CELERY_CREATE_LOGDIR -eq 1 ]; then
        create_default_dir "$CELERYD_LOG_DIR"
    fi
    if [ $CELERY_CREATE_RUNDIR -eq 1 ]; then
        create_default_dir "$CELERYD_PID_DIR"
    fi
}

create_paths() {
    create_default_dir "$CELERYD_LOG_DIR"
    create_default_dir "$CELERYD_PID_DIR"
}

export PATH="${PATH:+$PATH:}/usr/sbin:/sbin"


_get_pidfiles () {
    # note: multi < 3.1.14 output to stderr, not stdout, hence the redirect.
    ${CELERYD_MULTI} expand "${CELERYD_PID_FILE}" ${CELERYD_NODES} 2>&1
}


_get_pids() {
    found_pids=0
    my_exitcode=0

    for pidfile in $(_get_pidfiles); do
        local pid=`cat "$pidfile"`
        local cleaned_pid=`echo "$pid" | sed -e 's/[^0-9]//g'`
        if [ -z "$pid" ] || [ "$cleaned_pid" != "$pid" ]; then
            echo "bad pid file ($pidfile)"
            one_failed=true
            my_exitcode=1
        else
            found_pids=1
            echo "$pid"
        fi

    if [ $found_pids -eq 0 ]; then
        echo "${SCRIPT_NAME}: All nodes down"
        exit $my_exitcode
    fi
    done
}


_chuid () {
    su "$CELERYD_USER" -c "$CELERYD_MULTI $*"
}


start_workers () {
    if [ ! -z "$CELERYD_ULIMIT" ]; then
        ulimit $CELERYD_ULIMIT
    fi
    _chuid $* start $CELERYD_NODES $DAEMON_OPTS     \
                 --pidfile="$CELERYD_PID_FILE"      \
                 --logfile="$CELERYD_LOG_FILE"      \
                 --loglevel="$CELERYD_LOG_LEVEL"    \
                 $CELERY_APP_ARG                    \
                 $CELERYD_OPTS
}


dryrun () {
    (C_FAKEFORK=1 start_workers --verbose)
}


stop_workers () {
    _chuid stopwait $CELERYD_NODES --pidfile="$CELERYD_PID_FILE"
}


restart_workers () {
    _chuid restart $CELERYD_NODES $DAEMON_OPTS      \
                   --pidfile="$CELERYD_PID_FILE"    \
                   --logfile="$CELERYD_LOG_FILE"    \
                   --loglevel="$CELERYD_LOG_LEVEL"  \
                   $CELERY_APP_ARG                  \
                   $CELERYD_OPTS
}


kill_workers() {
    _chuid kill $CELERYD_NODES --pidfile="$CELERYD_PID_FILE"
}


restart_workers_graceful () {
    echo "WARNING: Use with caution in production"
    echo "The workers will attempt to restart, but they may not be able to."
    local worker_pids=
    worker_pids=`_get_pids`
    [ "$one_failed" ] && exit 1

    for worker_pid in $worker_pids; do
        local failed=
        kill -HUP $worker_pid 2> /dev/null || failed=true
        if [ "$failed" ]; then
            echo "${SCRIPT_NAME} worker (pid $worker_pid) could not be restarted"
            one_failed=true
        else
            echo "${SCRIPT_NAME} worker (pid $worker_pid) received SIGHUP"
        fi
    done

    [ "$one_failed" ] && exit 1 || exit 0
}


check_status () {
    my_exitcode=0
    found_pids=0

    local one_failed=
    for pidfile in $(_get_pidfiles); do
        if [ ! -r $pidfile ]; then
            echo "${SCRIPT_NAME} down: no pidfiles found"
            one_failed=true
            break
        fi

        local node=`basename "$pidfile" .pid`
        local pid=`cat "$pidfile"`
        local cleaned_pid=`echo "$pid" | sed -e 's/[^0-9]//g'`
        if [ -z "$pid" ] || [ "$cleaned_pid" != "$pid" ]; then
            echo "bad pid file ($pidfile)"
            one_failed=true
        else
            local failed=
            kill -0 $pid 2> /dev/null || failed=true
            if [ "$failed" ]; then
                echo "${SCRIPT_NAME} (node $node) (pid $pid) is down, but pidfile exists!"
                one_failed=true
            else
                echo "${SCRIPT_NAME} (node $node) (pid $pid) is up..."
            fi
        fi
    done

    [ "$one_failed" ] && exit 1 || exit 0
}


case "$1" in
    start)
        check_dev_null
        check_paths
        start_workers
    ;;

    stop)
        check_dev_null
        check_paths
        stop_workers
    ;;

    reload|force-reload)
        echo "Use restart"
    ;;

    status)
        check_status
    ;;

    restart)
        check_dev_null
        check_paths
        restart_workers
    ;;

    graceful)
        check_dev_null
        restart_workers_graceful
    ;;

    kill)
        check_dev_null
        kill_workers
    ;;

    dryrun)
        check_dev_null
        dryrun
    ;;

    try-restart)
        check_dev_null
        check_paths
        restart_workers
    ;;

    create-paths)
        check_dev_null
        create_paths
    ;;

    check-paths)
        check_dev_null
        check_paths
    ;;

    *)
        echo "Usage: /etc/init.d/${SCRIPT_NAME} {start|stop|restart|graceful|kill|dryrun|create-paths}"
        exit 64  # EX_USAGE
    ;;
esac

exit 0
```

```
root@OMS:/var/www/OpenMultiStack# cat /etc/default/celeryd
# Names of nodes to start
#   most people will only start one node:
CELERYD_NODES="worker1"
#   but you can also start multiple and configure settings
#   for each in CELERYD_OPTS (see `celery multi --help` for examples):
#CELERYD_NODES="worker1 worker2 worker3"
#   alternatively, you can specify the number of nodes to start:
#CELERYD_NODES=10

# Absolute or relative path to the 'celery' command:
#CELERY_BIN="/usr/local/bin/celery"
#CELERY_BIN="/virtualenvs/def/bin/celery"
CELERY_BIN="/var/www/OpenMultiStack/.pyenv/shims/celery"

# App instance to use
# comment out this line if you don't use an app
CELERY_APP="django_project"
# or fully qualified:
#CELERY_APP="proj.tasks:app"

# Where to chdir at start.
CELERYD_CHDIR="/var/www/OpenMultiStack/django_project/"

# Extra command-line arguments to the worker
CELERYD_OPTS="--time-limit=300 --concurrency=8"

# %N will be replaced with the first part of the nodename.
CELERYD_LOG_FILE="/var/www/OpenMultiStack/log/celery/%N.log"
CELERYD_PID_FILE="/var/www/OpenMultiStack/run/celery/%N.pid"

# Workers should run as an unprivileged user.
#   You need to create this user manually (or you can choose
#   a user/group combination that already exists, e.g. nobody).
CELERYD_USER="celery"
CELERYD_GROUP="celery"

# If enabled pid and log directories will be created if missing,
# and owned by the userid/group configured.
CELERY_CREATE_DIRS=1
```

```
adduser celery
```



## Issue

 * 著名なOpenStackプロバイダは1リージョンにつき20インスタンスまでの制限が存在する

## Wish

 * 複数のリージョンを意識することなくインスタンスを立ち上げたい
 * 複数のOpenStackプロバイダを意識することなくインスタンスを立ち上げたい
 * 複数クライアントから送出されるインスタンス立ち上げ命令、インスタンス破棄命令を集約したい
 * RESTFul APIでやり取りをしたい
 * 認証されたクライアントのみからの命令を処理したい

## Preparation for Development

 * install python 3.5.1

```
$ pyenv install 3.5.1
```

 * setting virtualenv for OpenMultiStack

```
$ pyenv virtualenv 3.5.1 OpenMultiStack
$ pyenv global OpenMultiStack
```

 * install related Django python module

```
$ pip install --upgrade pip
$ pip install django
$ pip install psycopg2 # djangoからpostgresqlを操作するために必要
$ pip install djangorestframework
$ pip install django-filter 
```

 * install openstack client

```
$ pip install python-openstackclient
```

## Create Django project and app

```
$ django-admin startproject django_project
$ cd django_project
$ python manage.py startapp open_multi_stack
$ tree
.
├── django_project
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-35.pyc
│   │   └── settings.cpython-35.pyc
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
└── open_multi_stack
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── migrations
    │   └── __init__.py
    ├── models.py
    ├── tests.py
    └── views.py

4 directories, 14 files
```

## Definition of the model

### open_stack_account 

 * [models.py](https://github.com/KosukeShimofuji/OpenMultiStack/blob/master/django_project/open_multi_stack/models.py)にモデルを定義していく。

### create migrate script 

```
$ python manage.py makemigrations open_multi_stack
Migrations for 'open_multi_stack':
  0001_initial.py:
    - Create model OpenStackAccount
```

### view sqlmigrate

```
$ python manage.py sqlmigrate open_multi_stack 0001
BEGIN;
--
-- Create model OpenStackAccount
--
CREATE TABLE "open_multi_stack_openstackaccount" ("id" serial NOT NULL PRIMARY KEY, "username" varchar(128) NOT NULL, "tenantname" varchar(128) NOT NULL, "tenant_id" varchar(128) NOT NULL, "password" varchar(128) NOT NULL, "auth_url" varchar(128) NOT NULL, "version" varchar(128) NOT NULL, "status" varchar(12) NOT NULL, "provider" varchar(128) NOT NULL);

COMMIT;
```

### execute migration

```
$ python manage.py migrate
Operations to perform:
  Apply all migrations: sessions, contenttypes, admin, auth, open_multi_stack
Running migrations:
  Rendering model states... DONE
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying open_multi_stack.0001_initial... OK
  Applying sessions.0001_initial... OK
```

### 作成されたテーブルの確認

```
$ psql -h127.0.0.1 -Udjango
ユーザ django のパスワード:
psql (9.4.8)
SSL接続(プロトコル: TLSv1.2, 暗号化方式: ECDHE-RSA-AES256-GCM-SHA384, ビット長: 256, 圧縮: オフ)
"help" でヘルプを表示します.

django=> \dt
                         リレーションの一覧
 スキーマ |                名前                 |    型    | 所有者
----------+-------------------------------------+----------+--------
 public   | auth_group                          | テーブル | django
 public   | auth_group_permissions              | テーブル | django
 public   | auth_permission                     | テーブル | django
 public   | auth_user                           | テーブル | django
 public   | auth_user_groups                    | テーブル | django
 public   | auth_user_user_permissions          | テーブル | django
 public   | django_admin_log                    | テーブル | django
 public   | django_content_type                 | テーブル | django
 public   | django_migrations                   | テーブル | django
 public   | django_session                      | テーブル | django
 public   | open_multi_stack_openstackaccount | テーブル | django
(11 行)

django=> \d open_multi_stack_openstackaccount
                                 テーブル "public.open_multi_stack_openstackaccount"
     列     |           型           |                                      修飾語
------------+------------------------+----------------------------------------------------------------------------------
 id         | integer                | not null default nextval('open_multi_stack_open_stack_account_id_seq'::regclass)
 username   | character varying(128) | not null
 tenantname | character varying(128) | not null
 tenant_id  | character varying(128) | not null
 password   | character varying(128) | not null
 auth_url   | character varying(128) | not null
 version    | character varying(128) | not null
 status     | character varying(12)  | not null
 provider   | character varying(128) | not null
インデックス:
    "open_multi_stack_open_stack_account_pkey" PRIMARY KEY, btree (id)
```

## 管理画面からデータベースを編集できるようにする

 * 管理アカウントの作成

```
$ python manage.py createsuperuser
Username (leave blank to use 'kosuke'): admin
Email address: kosuke.shimofuji@gmail.com
Password:
Password (again):
Superuser created successfully.
```

 * 作成したアカウント情報

```
admin:KraddInkasEatUljOundirbagphidab5
```

 * 開発用サーバの起動

```
$ python manage.py runserver 0.0.0.0:8000
```


 * 管理画面へのアクセス

http://openmultistack.test:8000/admin/

 * 管理画面のインデックスページ

![django admin index](https://raw.githubusercontent.com/KosukeShimofuji/OpenMultiStack/image/django_admin_index.png)

 * OpenStackAccountテーブルの編集ページ
 
![django admin openstackaccount edit page](https://raw.githubusercontent.com/KosukeShimofuji/OpenMultiStack/image/django_admin_edit_openstackaccount.png)

# 参考文献

 * http://www.openstack.org/
 * http://docs.djangoproject.jp/en/latest/topics/signals.html
 * https://remotestance.com/blog/1271/
 * http://qiita.com/nk_yohn3301/items/a68d8df18867e2c40449
 * https://www.conoha.jp/agreement/
 * http://docs.openstack.org/ja/api/quick-start/content/index.html#authenticate
 * http://qiita.com/kimihiro_n/items/86e0a9e619720e57ecd8
 * http://docs.openstack.org/ja/user-guide/sdk.html
 * http://unching-star.hatenablog.jp/entry/2015/12/02/113459#f-58c78a61
 * https://www.digitalocean.com/community/tutorials/how-to-run-django-with-mod_wsgi-and-apache-with-a-virtualenv-python-environment-on-a-debian-vps
 * http://hideharaaws.hatenablog.com/entry/2014/12/12/230825
 * http://docs.celeryproject.org/en/latest/tutorials/daemonizing.html#generic-init-scripts


