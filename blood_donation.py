import simpy as sp
import numpy as np
import statistics as st

# Parameters
RANDOM_SEED = 42
SIM_TIME = 8 * 60
min_interarrival = 1
max_interarrival = 10
NUM_TEST_STATIONS = 6
HISTORY_TEST_TIME = 5
SECOND_TEST_TIME = 5
NUM_NURSES = 8
NUM_SECOND_TEST_ROOMS = 4
BLOOD_PER_DONATION = 450
NUM_CHAIRS = 8

MIN_BLEED_TIME = 7
MAX_BLEED_TIME = 15
MIN_REST_TIME = 5
MAX_REST_TIME = 20

# Snack bar parameters
NUM_COOKIES = 100
SHOWN_COOKIES = 8
RESTOCK_TIME = 10
ODDS_OF_EATING_COOKIE_PER_FIVE_MINUTES = 0.3

class Donor_Centre(object):
    def __init__(self, env) -> None:
        self.env = env
        self.comp_station = sp.Resource(env, NUM_TEST_STATIONS)
        self.test_room = sp.Resource(env, NUM_SECOND_TEST_ROOMS)
        self.nurses = sp.Resource(env, NUM_NURSES)
        self.chair = sp.Resource(env, NUM_CHAIRS)
        
        self.cookies_availible = 8
        self.cookies_stored = 100

        self.donated_blood = 0
        self.total_donors = 0
        
    def check_in(self, donor_num):
        with self.comp_station.request() as req:
            yield req

            yield self.env.timeout(HISTORY_TEST_TIME)

    def second_test(self, donor_num):
        with self.test_room.request() as req:
            yield req

            yield self.env.timeout(SECOND_TEST_TIME)

    def draw_blood(self, donor_num):
        with self.chair.request() as req:
            yield req

            yield self.env.timeout(np.random.randint(MIN_BLEED_TIME, MAX_BLEED_TIME))
            self.donated_blood += BLOOD_PER_DONATION
            self.total_donors += 1

    def cookie_restock(self):

        if self.cookies_stored == 0 and self.cookies_availible == 0:
            return
        
        yield self.env.timeout(10)
        needed_for_restock = 8 - self.cookies_availible
        if self.cookies_stored >= needed_for_restock:
            self.cookies_availible = 8
            self.cookies_stored -= needed_for_restock
        else:
            self.cookies_availible += self.cookies_stored
            self.cookies_stored = 0

    def rest(self, donor_num):
        rest_time = np.random.randint(MIN_REST_TIME, MAX_REST_TIME)
        yield self.env.timeout(rest_time)
        cookie_eat_chances = rest_time // 5

        for _ in range(cookie_eat_chances):
            if np.random.rand() <= ODDS_OF_EATING_COOKIE_PER_FIVE_MINUTES and self.cookies_availible > 0:
                self.cookies_availible -= 1
                



def donate(env, centre):
    i = 1
    while True:
        env.process(centre.check_in(i))
        env.process(centre.second_test(i))
        env.process(centre.draw_blood(i))
        env.process(centre.rest(i))
        env.process(centre.cookie_restock())
        yield env.timeout(np.random.randint(min_interarrival, max_interarrival))
        i += 1
        

def main():
    env = sp.Environment()
    np.random.seed(RANDOM_SEED)

    centre = Donor_Centre(env)
    env.process(donate(env, centre))
    env.run(until=SIM_TIME)
    print(f"Total number of donors: {centre.total_donors}")
    print(f"Blood donated: {centre.donated_blood} mL")
    print("========================= Blood Canada is Closed for the day =========================")


if __name__ == '__main__':
    main()