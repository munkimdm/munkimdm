# How to Setup the Middleware Flask Application with uWSGI and Nginx on a AWS Ubuntu 18.04 instance

Building a Python application using the Flask microframework on Ubuntu 18.04. Using [uWSGI application server](http://uwsgi-docs.readthedocs.io/en/latest/) and how to launch the application and configure [Nginx](https://www.nginx.com/) to act as a front-end reverse proxy.

## Step 1 — Installing the Components from the Ubuntu Repositories

First step is to install all of the pieces that we need from the Ubuntu repositories. We will install `pip`, the Python package manager, to manage our Python components. We will also get the Python development files necessary to build uWSGI.

Update the local package index and install the packages that will allow us to build our Python environment.
   
`sudo apt update`
	
`sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools`

## Step 2 — Create a Python Virtual Environment

Next, set up a virtual environment to isolate the Flask application from the other Python files on the system.

Start by installing the `python3-venv` package, which will install the `venv` module:
    
`sudo apt install python3-venv`

Make the Flask app directory and go into it:    
`mkdir ~/flask`
`cd ~/flask`

Create a virtual environment to the Flask project’s Python requirements:
    
`python3.6 -m venv middleware`

This will install a local copy of Python and `pip` into a directory called `middleware` within your project directory.

Before installing applications within the virtual environment, you need to activate it. Do so by typing:
    
`source middleware/bin/activate`

Your prompt will change to indicate that you are now operating within the virtual environment. It will look like `(middleware)user@host:~/flask$`.

## Step 3 — Setting Up the Flask Application

You’re in the virtual environment, you can install Flask and uWSGI

First, let’s install `wheel` with the local instance of `pip` to ensure that our packages will install even if they are missing wheel archives:
    
`pip install wheel`

Next install Flask and uWSGI
    
`pip install uwsgi flask`

### Creating the Flask app

Now Flask is available, you can create the app. Flask is a microframework. It does not include many of the tools that more full-featured frameworks might, and exists mainly as a module that you can import into your projects to assist you in initializing a web application.

Create the Flask app in a single file, called `mdmauth.py`:
    
`nano ~/flask/mdmauth.py`

The application code will live in this file. It will import Flask and instantiate a Flask object. You can use this to define the functions that should be run when a specific route is requested:
    
	from flask import Flask
	app = Flask(__name__) 
		@app.route("/") def hello(): return "<h1 style='color:blue'>Hello There!</h1>" 
	if __name__ == "__main__": app.run(host='0.0.0.0') 

This basically defines what content to present when the root domain is accessed. Save and close the file when you’re finished.

## Setting up the Firewall

The firewall needs to be turned on with:

`sudo ufw enable`

**Very important**: after you enable the firewall, you need to allow port 22 and SSH to log back into your instance, if you don’t you will find yourself locked out of your AWS instance (speaking from experience)

To test the application, you need to allow access to port `5000`:
    
`sudo ufw allow 5000`

Now, you can test your Flask app by typing:
    
`python mdmauth.py`

You will see output like the following, including a helpful warning reminding you not to use this server setup in production:
    
	* Serving Flask app "myproject" (lazy loading)
	* Environment: production
	   WARNING: Do not use the development server in a production environment.
	   Use a production WSGI server instead.
	* Debug mode: off
	* Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)

Visit your server’s IP address followed by `:5000` in your web browser:
    
	http://97.79.XXX.XXX:5000 

You should see a “Hello There!” page

### The WSGI Entry Point

We need a file to serve as the entry point for the application. This will tell our uWSGI server how to interact with it.
    
`nano ~/flask/wsgi.py`

In this file, let’s import the Flask instance from our application and then run it:

`~/flask/wsgi.py`
    
    from mdmauth import app 
    if __name__ == "__main__": app.run() 

Save and close the file when you are finished.

## Step 4 — Configuring uWSGI

Your application is now written with an entry point established. We can now move on to configuring uWSGI.

### Testing uWSGI Serving

We can do this by simply passing it the name of our entry point. This is constructed by the name of the module (minus the `.py` extension) plus the name of the callable within the application. In our case, this is `wsgi:app`.

Let’s also specify the socket, so that it will be started on a publicly available interface, as well as the protocol, so that it will use HTTP instead of the `uwsgi` binary protocol. We’ll use the same port number, `5000`, that we opened earlier:
    
`uwsgi --socket 0.0.0.0:5000 --protocol=http -w wsgi:app`

Visit your server’s IP address with `:5000` appended to the end in your web browser again:
    
`http://97.79.XXX.XXX:5000`

You should see “Hello There!” again

When you have confirmed that it’s functioning properly, press `CTRL-C` in your terminal window.

You’re done now with the virtual environment setup. You can run `deactivate` to exit.

Any Python commands will now use the system’s Python environment again.

### Creating a uWSGI Configuration File

You have tested that uWSGI is able to serve your application, but ultimately you will want something more robust for long-term usage. 

uWSGI needs a `.ini` file for a more robust for long-term usage of the server over port 80
    
`nano ~/flask/middleware.ini`

Inside, we will start off with the `[uwsgi]` header so that uWSGI knows to apply the settings. We’ll specify two things: the module itself, by referring to the `wsgi.py` file minus the extension, and the callable within the file, `app`:
    
    [uwsgi] module = wsgi:app 

Next, we’ll tell uWSGI to start up in master mode and spawn five worker processes to serve actual requests:
    
    [uwsgi] module = wsgi:app master = true processes = 5 

When you were testing, you exposed uWSGI on a network port. However, you’re going to be using Nginx to handle actual client connections, which will then pass requests to uWSGI. Since these components are operating on the same computer, a Unix socket is preferable because it is faster and more secure. Let’s call the socket `middleware.sock` and place it in this directory.

Let’s also change the permissions on the socket. We’ll be giving the Nginx group ownership of the uWSGI process later on, so we need to make sure the group owner of the socket can read information from it and write to it. We will also clean up the socket when the process stops by adding the `vacuum` option:
    
    [uwsgi] module = wsgi:app master = true processes = 5 socket = myproject.sock chmod-socket = 660 vacuum = true 

The last thing we’ll do is set the `die-on-term` option. This can help ensure that the init system and uWSGI have the same assumptions about what each process signal means. Setting this aligns the two system components, implementing the expected behavior.

The final `.ini` file is:
    
    [uwsgi] 
    module = wsgi:app 
    master = true 
    processes = 5 
    
    socket = middleware.sock 
    chmod-socket = 660 
    vacuum = true 
    
    die-on-term = true 

You may have noticed that we did not specify a protocol like we did from the command line. That is because by default, uWSGI speaks using the `uwsgi` protocol, a fast binary protocol designed to communicate with other servers. Nginx can speak this protocol natively, so it’s better to use this than to force communication by HTTP.

When you are finished, save and close the file.

## Step 5 — Creating a systemd Unit File

Next, let’s create the systemd service unit file. Creating a systemd unit file will allow Ubuntu’s init system to automatically start uWSGI and serve the Flask application whenever the server boots.

Create a unit file ending in `.service` within the `/etc/systemd/system` directory to begin:
    
`sudo nano /etc/systemd/system/middleware.service`

Inside, we’ll start with the `[Unit]` section, which is used to specify metadata and dependencies. Let’s put a description of our service here and tell the init system to only start this after the networking target has been reached:
    
    [Unit] Description=uWSGI instance to serve myproject After=network.target 

Next, let’s open up the `[Service]` section. This will specify the user and group that we want the process to run under. Let’s give our regular user account ownership of the process since it owns all of the relevant files. Let’s also give group ownership to the `www-data` group so that Nginx can communicate easily with the uWSGI processes. Remember to replace the username here with your username:
    
    [Unit] Description=uWSGI instance to serve myproject After=network.target [Service] User=ubuntu Group=www-data 

Next, let’s map out the working directory and set the `PATH` environmental variable so that the init system knows that the executables for the process are located within our virtual environment. Let’s also specify the command to start the service. Systemd requires that we give the full path to the uWSGI executable, which is installed within our virtual environment. We will pass the name of the `.ini` configuration file we created in our project directory.

Remember to replace the username and project paths with your own information:
    
    [Unit] 
    Description=uWSGI instance to serve myproject After=network.target 
    
    [Service] 
    User=ubuntu 
    Group=www-data 
    WorkingDirectory=/home/ubuntu/middleware 
    Environment="PATH=/home/ubuntu/flask/middleware/bin" ExecStart=/home/ubuntu/flask/middleware/bin/uwsgi --ini middleware.ini 

Finally, let’s add an `[Install]` section. This will tell systemd what to link this service to if we enable it to start at boot. We want this service to start when the regular multi-user system is up and running:
    
    [Unit] 
    Description=uWSGI instance to serve myproject 
    After=network.target 
    
    [Service] 
    User=ubuntu 
    Group=www-data 
    WorkingDirectory=/home/ubuntu/middleware 
    Environment="PATH=/home/ubuntu/flask/middleware/bin" ExecStart=/home/ubuntu/flask/middleware/bin/uwsgi --ini middleware.ini 
    
    [Install] 
    WantedBy=multi-user.target 

With that, our systemd service file is complete. Save and close it now.

We can now start the uWSGI service we created and enable it so that it starts at boot:
    
`sudo systemctl start middleware`

`sudo systemctl enable middleware`

Let’s check the status:
    
`sudo systemctl status middleware`

You should see output like this:
    
	middleware.service - uWSGI instance to serve myproject 
	
	Loaded: loaded (/etc/systemd/system/middleware.service; enabled; vendor preset: enabled) 
	
	Active: active (running) since Fri 2018-07-13 14:28:39 UTC; 46s ago Main PID: 30360 (uwsgi) Tasks: 6 (limit: 1153) CGroup: /system.slice/middleware.service 
	├─30360 /home/ubuntu/flask/middleware/bin/uwsgi --ini middleware.ini 
	├─30378 /home/ubuntu/flask/middleware/bin/uwsgi --ini middleware.ini 
	├─30379 /home/ubuntu/flask/middleware/bin/uwsgi --ini middleware.ini 
	├─30380 /home/ubuntu/flask/middleware/bin/uwsgi --ini middleware.ini 
	├─30381 /home/ubuntu/flask/middleware/bin/uwsgi --ini middleware.ini 
	└─30382 /home/ubuntu/flask/middleware/bin/uwsgi --ini middleware.ini 

If you see any errors, be sure to resolve them before continuing with the tutorial. 

## Step 6 — Configuring Nginx to Proxy Requests

Our uWSGI application server should now be up and running, waiting for requests on the socket file in the project directory. Let’s configure Nginx to pass web requests to that socket using the `uwsgi` protocol.

Begin by creating a new server block configuration file in Nginx’s `sites-available` directory. Let’s call this `middleware` to keep in line with the rest of the guide:
    
`sudo nano /etc/nginx/sites-available/middleware`

Open up a server block and tell Nginx to listen on the default port `80`. Let’s also tell it to use this block for requests for our server’s domain name:

/etc/nginx/sites-available/flask
    
    server { 
    listen 80; 
    server_name munkimdm.domain.com; 
    } 

Next, let’s add a location block that matches every request. Within this block, we’ll include the `uwsgi_params` file that specifies some general uWSGI parameters that need to be set. We’ll then pass the requests to the socket we defined using the `uwsgi_pass` directive:

/etc/nginx/sites-available/middleware
    
    server { listen 80; server_name your_domain www.your_domain; location / { include uwsgi_params; uwsgi_pass unix:/home/ubuntu/flask/middleware.sock; } } 

Save and close the file when you’re finished.

To enable the Nginx server block configuration you’ve just created, link the file to the `sites-enabled` directory:
    
`sudo ln -s /etc/nginx/sites-available/middleware /etc/nginx/sites-enabled`

With the file in that directory, we can test for syntax errors by typing:
    
`sudo nginx -t`

If this returns without indicating any issues, restart the Nginx process to read the new configuration:
    
`sudo systemctl restart nginx`

Finally, let’s adjust the firewall again. We no longer need access through port `5000`, so we can remove that rule. We can then allow access to the Nginx server:
    
`sudo ufw delete allow 5000`

`sudo ufw allow 'Nginx Full'`

You should now be able to navigate to your server’s domain name in your web browser:
    
    http://97.79.XXX.XXX

You should see your application output:

![Flask sample app](https://assets.digitalocean.com/articles/nginx_uwsgi_wsgi_1404/test_app.png)

If you encounter any errors, trying checking the following:

  * `sudo less /var/log/nginx/error.log`: checks the Nginx error logs.
  * `sudo less /var/log/nginx/access.log`: checks the Nginx access logs.
  * `sudo journalctl -u nginx`: checks the Nginx process logs.
  * `sudo journalctl -u flask`: checks your Flask app’s uWSGI logs.

## Step 7 — Securing the Flask app

To ensure that traffic to your server remains secure, let’s get an SSL certificate for your domain from Let’s Encrypt.

- Add the Certbot Ubuntu repository:
    
`sudo add-apt-repository ppa:certbot/certbot`

Next, install Certbot’s Nginx package with `apt`:
    
`sudo apt install python-certbot-Nginx`

Certbot provides a variety of ways to obtain SSL certificates through plugins. The Nginx plugin will take care of reconfiguring Nginx and reloading the config whenever necessary. To use this plugin, type the following:
    
`sudo certbot --nginx -d munkimdm.domain.com`

This runs `certbot` with the `--nginx` plugin, using `-d` to specify the names we’d like the certificate to be valid for.

If this is your first time running `certbot`, you will be prompted to enter an email address and agree to the terms of service. After doing so, `certbot` will communicate with the Let’s Encrypt server, then run a challenge to verify that you control the domain you’re requesting a certificate for.

If that’s successful, `certbot` will ask how you’d like to configure your HTTPS settings.
    
    Output
    
    Please choose whether or not to redirect HTTP traffic to HTTPS, removing HTTP access. ------------------------------------------------------------------------------- 1: No redirect - Make no further changes to the webserver configuration. 2: Redirect - Make all requests redirect to secure HTTPS access. Choose this for new sites, or if you're confident your site works on HTTPS. You can undo this change by editing your web server's configuration. ------------------------------------------------------------------------------- Select the appropriate number [1-2] then [enter] (press 'c' to cancel): 

Select your choice then hit `ENTER`. The configuration will be updated, and Nginx will reload to pick up the new settings. `certbot` will wrap up with a message telling you the process was successful and where your certificates are stored:
    
    Output
    
    IMPORTANT NOTES: - Congratulations! Your certificate and chain have been saved at: /etc/letsencrypt/live/your_domain/fullchain.pem Your key file has been saved at: /etc/letsencrypt/live/your_domain/privkey.pem Your cert will expire on 2018-07-23. To obtain a new or tweaked version of this certificate in the future, simply run certbot again with the "certonly" option. To non-interactively renew *all* of your certificates, run "certbot renew" - Your account credentials have been saved in your Certbot configuration directory at /etc/letsencrypt. You should make a secure backup of this folder now. This configuration directory will also contain certificates and private keys obtained by Certbot so making regular backups of this folder is ideal. - If you like Certbot, please consider supporting our work by: Donating to ISRG / Let's Encrypt: https://letsencrypt.org/donate Donating to EFF: https://eff.org/donate-le 

If you followed the Nginx installation instructions in the prerequisites, you will no longer need the redundant HTTP profile allowance:
    
`sudo ufw delete allow 'Nginx HTTP'`

To verify the configuration, let’s navigate once again to your domain, using `https://`:
    
	https://munkimdm.domain.com

	You should see your application output once again, along with your browser’s security indicator, which should indicate that the site is secured. Woohoo!
	
## Step 8 — Crontab to auto renew SSL cert
	
Let’s Encrypt certificates are valid for 90 days only. It’s highly recommended that you run a cron job at least once a day to check if a renewal is necessary.

You can do a dry run to see if the command works:
    
	  sudo certbot renew --dry-run

Now we are going to set up a Cronjob to automatically check for renewals every day at 8am. 

### Open the crontab editor with:    
    sudo crontab -e

First time you start this it will ask you which editor to use. Select 1 for /bin/nano and paste the text below on the bottom. 

(You can later change editors with `/usr/bin/select-editor`)

### Paste the command at the end of the crontab file:
	0 8 * * * sudo certbot renew --post-hook "systemctl reload nginx"
	
	
### Here is simulated run of the crontab
	sudo certbot renew --dry-run --post-hook "systemctl reload nginx"
	Saving debug log to /var/log/letsencrypt/letsencrypt.log
	
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
	Processing /etc/letsencrypt/renewal/munkimdm.domain.com.conf
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
	Cert not due for renewal, but simulating renewal for dry run
	Plugins selected: Authenticator nginx, Installer nginx
	Renewing an existing certificate
	
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
	new certificate deployed with reload of nginx server; fullchain is
	/etc/letsencrypt/live/munkimdm.domain.com/fullchain.pem
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
	
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
	** DRY RUN: simulating 'certbot renew' close to cert expiry
	**          (The test certificates below have not been saved.)
	
	Congratulations, all renewals succeeded. The following certs have been renewed:
	  /etc/letsencrypt/live/munkimdm.domain.com/fullchain.pem (success)
	** DRY RUN: simulating 'certbot renew' close to cert expiry
	**          (The test certificates above have not been saved.)
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
	Running post-hook command: systemctl reload nginx

