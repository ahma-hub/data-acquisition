/* 
 # File: wrapper.c
 # Project: data-acquisition
 # Last Modified: 2021-8-2
 # Created Date: 2021-8-2
 # Copyright (c) 2021
 # Author: AHMA project (Univ Rennes, CNRS, Inria, IRISA)
 # Modified By: Duy-Phuc Pham (duy-phuc.pham@irisa.fr)
/****
  gcc wrapper.c -o wrapper -l bcm2835 -l pthread
 *****/
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <bcm2835.h>
#include <pthread.h>

#define PIN RPI_GPIO_P1_11
pthread_t t;

void *thread (void *arg) 
{
	char *cmd = arg; 	
	//printf("Executing ==> %s\n", cmd);
	bcm2835_gpio_write(PIN, HIGH);
	system(cmd);
}

void microsleep(int microseconds)  
{
	long usec = microseconds % 1000000;
	struct timespec ts_sleep;
	ts_sleep.tv_sec = microseconds / 1000000;
	ts_sleep.tv_nsec = 1000*usec;
	nanosleep(&ts_sleep, NULL);
}

int main(int argc, char *argv[]) 
{
	if (argc < 2) {
		printf("usage: %s cmd [duration] (us)\n", argv[0]);
		return 1;
	}
	if (!bcm2835_init()) {
		printf("error\n");
		return 1;
	}
	char *cmd = argv[1];
	bcm2835_gpio_fsel(PIN, BCM2835_GPIO_FSEL_OUTP);
	if(argc > 2) {
		pthread_create(&t, NULL, &thread, cmd);
		int duration = atoi(argv[2]);
		microsleep(duration);
		pthread_cancel(t);
	}
	else {
		bcm2835_gpio_write(PIN, HIGH);
		system(cmd);
	}
	bcm2835_gpio_write(PIN, LOW);
	bcm2835_close();
	return 0;
}

