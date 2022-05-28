from ortools.sat.python import cp_model
import numpy as np


NUM_SHIFTS_PER_DAY = 3    # this should not be modified at all time
NUM_DAYS_PER_WEEK = 7     # this should not be modified at all time
NUM_HOUR_PER_WEEK = 40    # this should not be modified at all time
NUM_FULL_TIME_WORKER = 2  # global variable that can be changed
NUM_PART_TIME_WORKER = 1  # also can be changed just a test number
NUM_DAY_OFF_PER_WEEK = 2  # each full time worker needs to have 2 days off

all_full_time_worker = range(NUM_FULL_TIME_WORKER)
all_worker = range(NUM_FULL_TIME_WORKER + NUM_PART_TIME_WORKER)
all_days = range(NUM_DAYS_PER_WEEK)
all_shifts = range(NUM_SHIFTS_PER_DAY)

assert NUM_SHIFTS_PER_DAY == 3, "the number of shifts per day has to be equal to 3"
assert NUM_DAYS_PER_WEEK == 7, "the number of days per week should always be 7"
assert NUM_HOUR_PER_WEEK == 40, "the number of hours to week should be equal to 40"


PART_TIME_PAY_RATE = 168

FULL_TIME_OVER_TIME_PAY = 167.5
PART_TIME_OVER_TIME_PAY = 225.12

num_worker_per_shift = [
    [3, 2, 4],  # Mon
    [3, 2, 4],  # Tue
    [3, 2, 4],  # Wed
    [3, 2, 4],  # Thu
    [3, 2, 4],  # Fri
    [3, 2, 4],  # Sat
    [3, 0, 0],  # Sun
]


model = cp_model.CpModel()

shifts = {}
worked_day = {}
for ft in all_worker:
    for day in all_days:
        worked_day[(ft, day)] = model.NewIntVar(0, 1, "worked_day[%i,%i]" % (ft, day))
        model.Add(worked_day[(ft, day)] == 0)
        for shift in all_shifts:
            shifts[(ft, day, shift)] = model.NewIntVar(0, 1, "shifts[%i,%i,%i]" % (ft, day, shift))
            b = model.NewBoolVar('b')
            model.Add(shifts[(ft, day, shift)] == 1).OnlyEnforceIf(b)
            model.Add(shifts[(ft, day, shift)] == 0).OnlyEnforceIf(b.Not())

            model.Add(worked_day[(ft, day)] == 1).OnlyEnforceIf(b)

shifts_flat = [shifts[ft, day, shift] for ft in all_worker for day in all_days for shift in all_shifts]


#
# constraint that the number of worker working is the same as the number needed
#
for day in all_days:
    for shift in all_shifts:
        num_worker_needed = num_worker_per_shift[day][shift]
        temp = [shifts[(ft, day, shift)] for ft in all_worker]
        num_working = sum(temp)
        model.Add(num_working == num_worker_needed)

#
# constraint that each full time worker needs to have 2 day off per week
# i = 0, 1 is full time worker
#
for ft in all_full_time_worker:
    day_work = model.NewIntVar(0, NUM_DAYS_PER_WEEK, "day_work")
    for day in all_days:
        temp = [shifts[(ft, day, shift)] for shift in all_shifts]
        b = model.NewBoolVar('b')
        model.Add(sum(temp) > 0).OnlyEnforceIf(b)
        model.Add(sum(temp) <= 0).OnlyEnforceIf(b.Not())
        model.Add(day_work == )
        if sum(temp) > 0:
            day_work += 1
    model.Add(day_work <= NUM_DAYS_PER_WEEK - NUM_DAY_OFF_PER_WEEK)

#
# calculate the number of hours work for each full time worker
# maximize the hours work for each full time worker
#
num_hour_work = 0
for ft in all_full_time_worker:
    temp = [shifts[(ft, day, shift)] for day in all_days for shift in all_shifts]
    num_hour_work += sum(temp) * 4
model.Minimize(NUM_FULL_TIME_WORKER * 40 - num_hour_work)
model.Add(NUM_FULL_TIME_WORKER * 40 - num_hour_work >= 0)

solver = cp_model.CpSolver()
status = solver.Solve(model)

#
# the result
#
if status == cp_model.OPTIMAL:
    print("Found the optimal solution")
    for day in all_days:
        for shift in all_shifts:
            print("the schedule for shift {} day {}".format(shift, day))
            for worker in all_worker:
                if solver.Value(shifts[(worker, day, shift)]) == 1:
                    print("Worker {} is working today".format(worker))





