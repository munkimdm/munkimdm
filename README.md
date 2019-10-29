# munkimdm
Flask app for connecting [Munki](https://github.com/munki/munki) and [MicroMDM](https://github.com/micromdm/micromdm).

## Background reading:

* [Creating MunkiMDM Part I](https://joncrain.github.io/2018/11/01/micromdm_munki.html)
* [Creating MunkiMDM Part II](https://joncrain.github.io/2018/11/06/micromdm_munki_partii.html)
* [Creating MunkiMDM Part III](https://joncrain.github.io/2018/11/08/micromdm_munki_partiii.html)
* [MunkiMDM Update](https://joncrain.github.io/2019/01/29/micromdm_munki_update.html)

## Running with Docker
To run the Flask application within Docker, all that is required is the following:

    docker build -t munkimdm .
    docker run -d -p 5000:5000 munkimdm

Afterwards, you can check on the status of the container using `docker ps`:

    $ docker ps
    CONTAINER ID        IMAGE               COMMAND                CREATED             STATUS              PORTS                              NAMES
    3e247bae5347        munkimdm            "python munkimdm.py"   1 second ago        Up 1 second         0.0.0.0:5000->5000/tcp, 8080/tcp   serene_fermat

And view the logs of the container using `docker logs <container>`:

     $ docker logs 3e247bae5347
     * Serving Flask app "munkimdm" (lazy loading)
     * Environment: production
       WARNING: This is a development server. Do not use it in a production deployment.
       Use a production WSGI server instead.
     * Debug mode: on
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
     * Restarting with stat
     * Debugger is active!
     * Debugger PIN: 158-656-488

