# How to setup OTW/SSL for tests

## Linux:
### Generating private key with passwords

1. To generate a private key with password run: 

```openssl genrsa -aes256 -out {path}/key.pem 2048```

2. Type your password and verify it when asked.
3. The output file will be created in dir where you declare in key.pem file.

### Requesting a key

1. To request a key, on the command line run:

    ```openssl req -new -key {path}/key.pem -out {path}/csr.pem -config openssl.cnf```
2. Type the password you set previously.
3. When asked for information, you don't need to be specific. You can use anything@somewhere.invalid as email because real emails can cause issues.
4. The file csr.pem is created in the {path} folder.

### Signing the key

1. To sign the key request file with your private key, on the command line run:

```openssl req -x509 -days 3650 -key {path}/key.pem -in {path}/csr.pem -out {path}/ibservercafile.pem```

2. Type the password you set before.
3. The file ibservercafile.pem is created on the {path} folder. Use this file on your clients.

### Creating the server side file

1. On the command line, go to the {path} folder.
2. Add ibservercafile to your private key file. On the command line run:

```cat ibservercafile.pem + key.pem > ibserverCAfile.pem```
3. Move "ibserverCAfile.pem" file to dir with Interbase Python Driver test/files.
4. In order to use the server_public_path argument for ssl connection the file should be put into a separate directory and renamed using c_rehash command:
```
cd /some/where/certs
c_rehash .
```

### Configuring InterBase

1. Make sure the InterBase server is stopped.
2. Search for the file ibss_config.default. For example: opt/interBase/secure/server
3. Open Notepad or other text editor as Administrator.
4. Type the following text and use the password you set previously: 

```
    IBSSL_SERVER_PORT_NO=3065
    IBSSL_SERVER_CERTFILE="{path to driver}/test/files"
    IBSSL_SERVER_PASSPHRASE=<password>
```

This case only for tests!

5. Save the file as ibss_config and place it in the same folder as ibss_config.default
6. Open a text editor as Administrator and open the file `services` located in the `etc` folder.
7. Add the following line at the bottom: ``` gds_ssl       3065/tcp          #InterBase SSL Server```.
8. Save and close the file.
9. Start InterBase server.

### Starting tests for embedded version of InterBase

1. In order to run all unit tests with embedded version of InterBase, 
please, uncomment the following line in the file constants.py:
```# os.environ['IBTEST_USE_EMBEDDED'] = 'True'```

## Windows

For setup OTW/SSL on Windows you can use: https://docwiki.embarcadero.com/InterBase/2020/en/Setup_OTW/SSL_and_InterBase

It is important to move `ibserverCAfile.pem` to {path to driver}/test/files folder.
