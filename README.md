# OpenMultiStack

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
```

## Create Django project



# 参考文献

 * http://www.openstack.org/
 * http://docs.djangoproject.jp/en/latest/topics/signals.html
 * https://remotestance.com/blog/1271/
 * http://qiita.com/nk_yohn3301/items/a68d8df18867e2c40449
 * https://www.conoha.jp/agreement/
 * http://docs.openstack.org/ja/api/quick-start/content/index.html#authenticate

