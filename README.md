# SINDIT - SINTEF Digital Twin

## Description

### This work

### Original SINDIT project

This work builds upon the architecture proposal presented at the [ICSA22 conference](https://icsa-conferences.org/2022/conference-tracks/new-and-emerging-ideas/)

[Watch the presentation here](https://www.youtube.com/watch?v=ExHNP6527d8&list=PLmMTZhDUcVmuFcJG9tbxR6AAWcOl2Jej3&index=29&t=2s)

*Cite the work:*

```
@inproceedings{waszak2022ICSA,
  title={Let the Asset Decide: Digital Twins with Knowledge Graphs},
  author={Waszak, Maryna and Lam, An Ngoc and Hoffmann, Volker and Elvesæter, Brian and Mogos, Maria Flavia and Roman, Dumitru},
  booktitle={IEEE 19th International Conference on Software Architecture Companion (ICSA-C)},
  year={2022}
}
```

## Development setup
For this project, a devcontainer-setup for Visual Studio Code is implemented. It can be used together with SSH remote development if needed.

##### Requirements:
- Recent Linux operating system, e.g. Debian 11 (Some used DBMS-versions (Neo4J) are incompatible with, for example older CentOS systems)
- Docker and docker-compose installed

##### Development setup:
1. Check out this repository on the execution device (remote or local)
2. Open the folder on the development-client (local or with the VS Code remote development extension via SSH)
3. Reopen the folder as container with the remote containers extension
4. Reload the window after the container is fully loaded (as suggested by the initialization script, to apply the installed modules for auto-corrections)
5. Start the development databases manually with `docker-compose -f docker-compose.dev.yml up -d`

After this, use the run and debug functionalities of the IDE to execute the separate services. The run configuration is already set up in this repository.

If the DT-instance was not previously initialized, run the initialization script. E.g. via the run configuration `Learning factory instance: initialization`.

##### Code formatting:
The python formatting "black" is utilized and enforced by the IDE configuration. Auto-formatting is performed at every file-saving.

## Deployment and execution
This project is deployed via docker-compose. Run `docker-compose up -d` to start the digital twin with all required services.

If the DT-instance was not previously initialized, run the initialization scripts as described below (DT learning factory initialization script).

For the learning factory example, remember to access the VPN / make a port mappig via Teleport tsh in order to get an actual connection!

 

For updating the DT after pushing to the deployment branch, run manually on the workstation: `docker-compose down && git pull && sudo chmod 777 -R docker_mounted_storage && docker-compose build && docker-compose up -d`.

## Exposed interfaces:

**Dashboard**

The main user interface (dashboard) of the digital twin can be reached at [http://localhost:8050/](http://localhost:8050/). 

**REST API**
The REST API is availlable at [http://localhost:8000/](http://localhost:8000/). 
Swagger documentation is availlable at [http://localhost:8000/docs](http://localhost:8000/docs). 
 
Webinterfaces of the used DBMS are available at  [http://localhost:7475/](http://localhost:7475/) (Neo4J) and  [http://localhost:8087/](http://localhost:8087/) (InfluxDB).

## Services:

In addition to the DBMS systems, the DT includes following services and scripts:

### DT-Backend service:

Sets up the realtime connections (OPC UA, MQTT) to persist timeseries data. Provides a REST API to access the assets of the factory including e.g. timeseries data (current and historic).

### DT-Frontend service:

Provides a dashboard and visualization of the DT via a web interface at [http://localhost:8050/](http://localhost:8050/). Utilizes the REST API

### Similarity-Pipeline:

coming soon

## DT learning factory initialization script:

Initializes the DT for the fischertechnik learning factory. Execute inside the DT-Backend container after starting all services via: 

`docker-compose exec sindit_dt_backend python init_learning_factory_from_cypher_file.py`

After this, for the DT-services to connect to the newly created timeseries connections, restart the services with `docker-compose restart sindit_dt_backend sindit_dt_frontend` (simply restarting all containers does lead to the dependencies for database access not being resolved).

## References

coming soon

## Blame & Contact

- Timo Peter [<timo.peter@sintef.no>](mailto:timo.peter@sintef.no)
