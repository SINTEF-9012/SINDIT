# SINDIT - SINTEF Digital Twin

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

## Deployment
This project is deployed via docker-compose. Run `docker-compose up -d` to start the digital twin with all required services.

If the DT-instance was not previously initialized, run `docker-compose exec sindit_dt_backend python init_learning_factory_from_cypher_file.py`. After this, for the DT-services to connect to the newly created timeseries connections, restart the services with `docker-compose 



## Description
This work has bee presented at the [ICSA22 conference](https://icsa-conferences.org/2022/conference-tracks/new-and-emerging-ideas/)

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


![description](assets/description_sindit.PNG)

### Chocolate Production Process

Here, we have several steps before the chocolate bars can be moulded and finally wrapped. The process starts with conching ground sugar with melted cocoa butter. Through tempering of the chocolate it obtains the sheen and crisp properties that we all know from chocolate bars.

<img src="assets/fac_pics.jpg" alt="Picture1" style="zoom:20%; background-color: white" />



### Modelling the Chocolate Factory

This is a simplified digital model of the chocolate factory. M1-M5 are machines with sensors S1-S5. Between the machines the ingredients are stored in queues Q1-Q9. At the last queue Q9 the packaged chocolate bars are modelled as pink squares P1-P3.

<img src="assets/fac_schema.jpg" alt="Picture2" style="zoom:20%; background-color: white" />

## **Requirements**

### System:

1. Docker compose

If you are using windows see [here](https://docs.microsoft.com/en-gb/windows/wsl/install-win10#step-4---download-the-linux-kernel-update-package)

### Local deployment of example factory:

2. Build the Docker containers

   ```sh
   docker compose build
   ```

3. Start up the Docker containers

    ```sh
	docker compose up
	```

4. The example dash board of a chocolate factory can be reached at [http://localhost:8050/](http://localhost:8050/)


![dash](assets/fac_dashboard.JPG)

To start the simulation enter the simulation duration and press 'Simulate'. With 'Reset' the original state of the factory graph can be restored.

### Local development

1. **Data layer: Databases** 

   Start the databases and required services via docker-compose:

       ```sh
       docker-compose up influx_db zoo kafka neo4jfactory neo4jparts
      ```

2. Load the factory graph into the Neo4j database:

   ```sh
    python ./chocolate_factory.py
   ```

3. **Application layer** including the sensor connectors and REST API

   Directly start service.py within your IDE / debugger
   
4. **Presentation layer: Plotly Dash**

   Directly start presentation.py within your IDE / debugger

## References

1. [simpy](https://pypi.org/project/simpy/)

## Blame & Contact

- Maryna Waszak [<maryna.waszak@sintef.no>](mailto:maryna.waszak@sintef.no)
