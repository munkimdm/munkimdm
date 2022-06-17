# MunkiMDM
Flask app for connecting [Munki](https://github.com/munki/munki) and [MicroMDM](https://github.com/micromdm/micromdm).

## Background reading:

* [Creating MunkiMDM Part I](https://joncrain.github.io/2018/11/01/micromdm_munki.html)
* [Creating MunkiMDM Part II](https://joncrain.github.io/2018/11/06/micromdm_munki_partii.html)
* [Creating MunkiMDM Part III](https://joncrain.github.io/2018/11/08/micromdm_munki_partiii.html)
* [MunkiMDM Update](https://joncrain.github.io/2019/01/29/micromdm_munki_update.html)

## Install, update, remove profiles and Mac App Store apps using script-only pkginfo files

Simple scripts to run API commands that give Munki back functionality that now are MDM only actions:

* Install system level configuration mobileconfig profiles.
* Leverage Munki `install_chec![MunkiMDM 012](https://user-images.githubusercontent.com/7052526/174392063-f6027b9a-b679-40b6-9adf-52a671511b29.png)
ks` scripts where we can build in logic to run commands or install apps based on a set criteria or to even maintain a machine state on an hourly basis.
* Granular manifests, giving us the power to go granular to one machine, to a group of machines, or to the entire fleet as we so choose with an item.  
* Install volume purchased apps from the App Store without the need to maintain the pkgs in the repo. 
* All other Munki pkginfo keys goodies such as target an architecture `arm64` key

The only secret keys that travels through munki's scripts are the middleware user and password in BasicAuth format which can be easily updated and changed and even set to be in a rotation schedule.

![MunkiMDM 006](https://user-images.githubusercontent.com/7052526/174391942-e2b676d4-7ec1-4810-aa72-5329ec76fb12.png)
