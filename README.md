# SINDIT - SINTEF Digital Twin

## Description

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


## References

1. [simpy](https://pypi.org/project/simpy/)

## Blame & Contact

- Maryna Waszak [<maryna.waszak@sintef.no>](mailto:maryna.waszak@sintef.no)
