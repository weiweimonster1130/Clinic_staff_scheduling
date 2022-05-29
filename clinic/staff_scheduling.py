from ortools.sat.python import cp_model
import numpy as np

NUM_SHIFTS_PER_DAY = 3  # this should not be modified at all time
NUM_DAYS_PER_WEEK = 7  # this should not be modified at all time
NUM_HOUR_PER_WEEK = 40  # this should not be modified at all time
NUM_FULL_TIME_WORKER = 2  # global variable that can be changed
NUM_PART_TIME_WORKER = 1  # also can be changed just a test number
NUM_DAY_OFF_PER_WEEK = 2  # each full time worker needs to have 2 days off

# use regularization to decrease the tightness to prevent too much overtime pay

all_full_time_worker = range(NUM_FULL_TIME_WORKER)
all_worker = range(NUM_FULL_TIME_WORKER + NUM_PART_TIME_WORKER)
all_days = range(NUM_DAYS_PER_WEEK)
all_shifts = range(NUM_SHIFTS_PER_DAY)

assert NUM_SHIFTS_PER_DAY == 3, "the number of shifts per day has to be equal to 3"
assert NUM_DAYS_PER_WEEK == 7, "the number of days per week should always be 7"
assert NUM_HOUR_PER_WEEK == 40, "the number of hours to week should be equal to 40"

PART_TIME_PAY_RATE = -10       #  needs to be 168

FULL_TIME_OVER_TIME_PAY = 167.5
PART_TIME_OVER_TIME_PAY = 225.12

TOTAL_NUM_HOURS = 70

num_worker_and_hours_per_shift_normal = [
    [(3, 4), (2, 3.5), (4, 3.5)],  # Mon
    [(3, 4), (2, 3.5), (4, 3.5)],  # Tue
    [(3, 4), (2, 3.5), (4, 3.5)],  # Wed
    [(3, 4), (2, 3.5), (4, 3.5)],  # Thu
    [(3, 4), (2, 3.5), (4, 3.5)],  # Fri
    [(3, 4), (2, 3.5), (4, 3.5)],  # Sat
    [(3, 4), (2, 3.5), (4, 3.5)],  # Sun
]

num_worker_and_hours_per_shift_adjusted = [
    [(3, 4), (2, 3.15), (4, 3.5)],  # Mon
    [(3, 4), (2, 3.15), (4, 3.5)],  # Tue
    [(3, 4), (2, 3.15), (4, 3.5)],  # Wed
    [(3, 4), (2, 3.15), (4, 3.5)],  # Thu
    [(3, 4), (2, 3.15), (4, 3.5)],  # Fri
    [(3, 4), (2, 3.15), (4, 3.5)],  # Sat
    [(3, 4), (2, 3.15), (4, 3.5)],  # Sun
]

model = cp_model.CpModel()

shifts = {}
worked_day = {}


class StaffScheduleSolutionPrinter(cp_model.CpSolverSolutionCallback):
    """
    Print intermediate solutions
    """
    def __init__(self):
        cp_model.CpSolverSolutionCallback.__init__(self)
        # self.__variables = variables
        self.__solution_count = 0

    def on_solution__callback(self):
        self.__solution_count += 1
        print("This an intermediate solution")
        for day in all_days:
            for shift in all_shifts:
                print("the schedule for shift {} day {}".format(shift, day))
                for worker in all_worker:
                    if solver.Value(shifts[(worker, day, shift)]) == 1:
                        print("Worker {} is working today".format(worker))


for ft in all_worker:
    for day in all_days:
        worked_day[(ft, day)] = model.NewIntVar(0, 1, "worked_day[%i,%i]" % (ft, day))
        model.Add(worked_day[(ft, day)] == 0)
        for shift in all_shifts:
            shifts[(ft, day, shift)] = model.NewIntVar(0, 1, "shifts[%i,%i,%i]" % (ft, day, shift))
            '''
             if shifts[(ft, day, drift)] == 1:
                   worked_day[(ft, day)] = 1
            '''
            # b = model.NewBoolVar('b')
            # model.Add(shifts[(ft, day, shift)] == 1).OnlyEnforceIf(b)
            # model.Add(shifts[(ft, day, shift)] == 1).OnlyEnforceIf(b.Not())
            # model.Add(worked_day[(ft, day)] == 1).OnlyEnforceIf(b)
            # model.Add(shifts[(ft, day, shift)] == 1).OnlyEnforceIf(b.Not())
#
# constraint that the number of worker working is the same as the number needed
#
for day in all_days:
    for shift in all_shifts:
        num_worker_needed = num_worker_and_hours_per_shift_normal[day][shift][0]
        temp = [shifts[(ft, day, shift)] for ft in all_worker]
        num_working = sum(temp)
        model.Add(num_working == num_worker_needed)

#
# constraint that each full time worker needs to have 2 day off per week
# i = 0, 1 is full time worker
#
# for ft in all_full_time_worker:
#     temp = [worked_day[(ft, day)] for day in all_days]
#     model.Add(sum(temp) <= NUM_DAYS_PER_WEEK - NUM_DAY_OFF_PER_WEEK)

#
# Easy Constraint that every full time has to work less than 10 hour a day
#


# for day in all_days:
#     for ft in all_full_time_worker:
#         shift_hours_worked = []
#         for shift in all_shifts:
#             shift_hours_worked.append(
#                 int(num_worker_and_hours_per_shift_normal[day][shift][1] * 2) * shifts[(ft, day, shift)]
#             )
#
#         model.Add(sum(shift_hours_worked) <= 10)

#
# calculate the number of hours work for each full time worker
# maximize the hours work for each full time worker
# make sure the total hour work per person is less than 40
#
ft_hour_work_per_week = []
for ft in all_full_time_worker:
    temp = []
    for shift in all_shifts:
        for day in all_days:
            temp.append(int(num_worker_and_hours_per_shift_normal[day][shift][1] * 2) * shifts[(ft, day, shift)])
    ft_hour_work_per_week.append(sum(temp))

for hour_work in ft_hour_work_per_week:
    model.Add(hour_work <= NUM_HOUR_PER_WEEK * 2)

part_time_total_hour = model.NewIntVar(0, TOTAL_NUM_HOURS, 'part_time_hour')
model.Add(part_time_total_hour == NUM_HOUR_PER_WEEK - sum(ft_hour_work_per_week))
# model.Minimize(part_time_total_hour * PART_TIME_PAY_RATE)

solver = cp_model.CpSolver()
solution_printer = StaffScheduleSolutionPrinter()
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
print(status)
