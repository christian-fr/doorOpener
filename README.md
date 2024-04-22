For server:
```shell
python3 -m pip install -r requirements_server.txt
sudo mkdir /etc/doorOpener
$ cp ./sh/server/.env_actor_example /etc/doorOpener/.env_server
$ cp ./sh/util/.env_mail_example /etc/doorOpener/.env_mail
$ nano /etc/doorOpener/.env_server

```

For actor/client:
```shell
sudo mkdir /etc/doorOpener
$ cp ./sh/actor/.env_actor_example /etc/doorOpener/.env_actor
$ cp ./sh/util/.env_mail_example /etc/doorOpener/.env_mail
$ nano /etc/doorOpener/.env_actor
```
