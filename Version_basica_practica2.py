"""
Solution to the one-way tunnel
"""
import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

SOUTH = 1
NORTH = 0

NCARS = 30
NPED = 10
TIME_CARS_NORTH = 0.5  # a new car enters each 0.5s
TIME_CARS_SOUTH = 0.5  # a new car enters each 0.5s
TIME_PED = 5 # a new pedestrian enters each 5s
TIME_IN_BRIDGE_CARS = (1, 0.5) # normal 1s, 0.5s
TIME_IN_BRIDGE_PEDESTRIAN = (30, 10) # normal 1s, 0.5s

class Monitor():
    
    def __init__(self):
        self.mutex = Lock()
        self.patata = Value('i', 0)
        
# Definimos variables correspondientes L número de coches de una dirección determinada/peatones que se encuentran en el puente    
        self.coches_norte = Value('i', 0) # número de coches que se dirigen al norte
        self.coches_sur = Value('i', 0) # número de coches que se dirigen al sur
        self.peatones = Value('i', 0) # número de peatones
   

# Definimos las variables condición, que habrá una por cada proceso
        self.N_puede_pasar = Condition(self.mutex)
        self.S_puede_pasar = Condition(self.mutex)
        self.P_puede_pasar = Condition(self.mutex)
 
        
# Ahora definimos métodos que indiquen si quedan coches norte/sur o peatones en el puente

    def no_hay_coches_N(self) :
        return self.coches_norte.value == 0
    
    def no_hay_coches_S(self) :
        return self.coches_sur.value == 0
    
    def no_hay_peatones(self) :
        return self.peatones.value == 0
    
    
# A continuación definimos los métodos que determinen si se permite el paso
    
    def coches_N_pueden_pasar(self) :
        return (self.no_hay_coches_S() and self.no_hay_peatones())
    
    def coches_S_pueden_pasar(self) :
        return (self.no_hay_coches_N() and self.no_hay_peatones())
        
    def peatones_pueden_pasar(self) :
        return (self.no_hay_coches_S() and self.no_hay_coches_N())
    
   
    
    def wants_enter_car(self, direction: int) -> None:
        self.mutex.acquire()
        self.patata.value += 1
      
# Distinguimos 2 casos: si los coches se dirigen al norte o al sur
        if direction == SOUTH :
            
             self.S_puede_pasar.wait_for(self.coches_S_pueden_pasar) #Comprobamos si el coche puede pasar el puente                  
             self.coches_sur.value += 1 # le sumamos 1 a los coches acumulados en el puente
             
        else :
            
             self.N_puede_pasar.wait_for(self.coches_N_pueden_pasar) #Comprobamos si el coche puede pasar el puente                  
             self.coches_norte.value += 1 # le sumamos 1 a los coches acumulados en el puente            
                          
        self.mutex.release()


    
    def leaves_car(self, direction: int) -> None:
        self.mutex.acquire() 
        self.patata.value += 1
        
# Volvemos a distinguir en función de la dirección
        if direction == SOUTH :
            self.coches_sur.value -= 1 #Al salir del puente el numero de coches en dicho puente disminuye en 1

            if self.coches_sur.value == 0 :
                self.N_puede_pasar.notify_all()
                self.P_puede_pasar.notify_all()     
            
        else: 
            
            self.coches_norte.value -= 1 #Al salir del puente el numero de coches en dicho puente disminuye en 1
                      
            if self.coches_norte.value == 0 :
                self.S_puede_pasar.notify_all()
                self.P_puede_pasar.notify_all() 

        self.mutex.release()

    def wants_enter_pedestrian(self) -> None:
        self.mutex.acquire()
        self.patata.value += 1
        self.P_puede_pasar.wait_for(self.peatones_pueden_pasar)
        self.peatones.value += 1
        self.mutex.release()

    def leaves_pedestrian(self) -> None:
        self.mutex.acquire()
        self.patata.value += 1
        self.peatones.value -= 1
        
        if self.peatones == 0 :
            self.N_puede_pasar.notify_all()
            self.S_puede_pasar.notify_all() 
                
        self.mutex.release()

    def __repr__(self) -> str:
        return f'Monitor: {self.patata.value}'

def delay_car_north(factor = 4) -> None:
    time.sleep(random.random()/factor)

def delay_car_south(factor = 4) -> None:
    time.sleep(random.random()/factor)

def delay_pedestrian(factor = 2) -> None:
    time.sleep(random.random()/factor) 

def car(cid: int, direction: int, monitor: Monitor)  -> None:
    print(f"car {cid} heading {direction} wants to enter. {monitor}")
    monitor.wants_enter_car(direction)
    print(f"car {cid} heading {direction} enters the bridge. {monitor}")
    if direction==NORTH :
        delay_car_north()
    else:
        delay_car_south()
    print(f"car {cid} heading {direction} leaving the bridge. {monitor}")
    monitor.leaves_car(direction)
    print(f"car {cid} heading {direction} out of the bridge. {monitor}")

def pedestrian(pid: int, monitor: Monitor) -> None:
    print(f"pedestrian {pid} wants to enter. {monitor}")
    monitor.wants_enter_pedestrian()
    print(f"pedestrian {pid} enters the bridge. {monitor}")
    delay_pedestrian()
    print(f"pedestrian {pid} leaving the bridge. {monitor}")
    monitor.leaves_pedestrian()
    print(f"pedestrian {pid} out of the bridge. {monitor}")



def gen_pedestrian(monitor: Monitor) -> None:
    pid = 0
    plst = []
    for _ in range(NPED):
        pid += 1
        p = Process(target=pedestrian, args=(pid, monitor))
        p.start()
        plst.append(p)
        time.sleep(random.expovariate(1/TIME_PED))

    for p in plst:
        p.join()

def gen_cars(direction: int, time_cars, monitor: Monitor) -> None:
    cid = 0
    plst = []
    for _ in range(NCARS):
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        plst.append(p)
        time.sleep(random.expovariate(1/time_cars))

    for p in plst:
        p.join()

def main():
    monitor = Monitor()
    gcars_north = Process(target=gen_cars, args=(NORTH, TIME_CARS_NORTH, monitor))
    gcars_south = Process(target=gen_cars, args=(SOUTH, TIME_CARS_SOUTH, monitor))
    gped = Process(target=gen_pedestrian, args=(monitor,))
    gcars_north.start()
    gcars_south.start()
    gped.start()
    gcars_north.join()
    gcars_south.join()
    gped.join()


if __name__ == '__main__':
    main()
