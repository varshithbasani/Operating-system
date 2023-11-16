import dearpygui.dearpygui as dpg
import time
import sys
dpg.create_context()



class Queue:
    def __init__(self, queueType=None):
        self.queue = [] 
        self.queueType = queueType

    def __str__(self):
        return ",".join([str(pcb.pid) for pcb in self.queue])

    def addPCB(self, pcb):
        self.queue.append(pcb)

    def removePCB(self):
        item = self.queue[0]
        del self.queue[0]
        return item

    def decrement(self):
        """ Iterate over the self.queue and decrement or call whatever
            method for each of the pcb's in this queue
        """
        # for each process in queue
        #    call decrementIoBurst

        for pcb in self.queue:
            pcb.decrementIoBurst()

    def incrememnt(self, what='waittime'):
        """ Iterate over the self.queue and decrement or call whatever
            method for each of the pcb's in this queue
        """
        # for each process in queue
        #    call incrementwaittime
        if what == 'waittime':
            for pcb in self.queue:
                pcb.incrementwaitQueueTime()
        elif what == 'runtime':
            for pcb in self.queue:
                pcb.incrementreadyQueueTime()

class SysClock:
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state
        if not 'clock' in self.__dict__:
            self.clock = 0

    def increment(self):
        self.clock += 1

    def getClock(self):
        return self.clock

class CPU:
    def __init__(self):
        self.busy = False
        self.runningPCB = None
        self.executionTime = 0

    def incrementExecutionTime(self):
        self.executionTime += 1

    def decrementCurrentProcess(self):
        self.runningPCB.decrementCpuBurst()

    def loadProcess(self, pcb):
        self.runningPCB = pcb

    def KickOff(self):
        if self.runningPCB.getCurrentBurstTime() == 0:
            self.busy = False
            item = self.runningPCB
            self.runningPCB = None
            return item
        
class IO:
    def __init__(self) -> None:
        self.busy = False
        self.servingPCB = None
    
    def decrementCurrentProcess(self):
        self.servingPCB.decrementIoBurst()
    
    def loadProcess(self, pcb):
        self.servingPCB = pcb
    
    def KickOff(self):
        if self.servingPCB.getCurrentBurstTime() == 0:
            self.busy = False
            item = self.servingPCB
            self.servingPCB = None
            return item

class PCB:
    def __init__(self, pid, bursts, at, priority):
        self.pid = pid
        self.priority = priority     # 0
        self.arrivalTime = at
        self.bursts = bursts
        self.currBurst = 'CPU'
        self.currBurstIndex = 0
        self.cpuBurst = 5
        self.readyQueueTime = 0
        self.waitQueueTime = 0
        self.TAT = 0

    def decrementCpuBurst(self):
        self.bursts[self.currBurstIndex] -= 1

    def decrementIoBurst(self):
        self.bursts[self.currBurstIndex] -= 1

    def incrementBurstIndex(self):
        self.currBurstIndex += 1

    def incrementreadyQueueTime(self):
        self.readyQueueTime += 1

    def incrementwaitQueueTime(self):
        self.waitQueueTime += 1

    def getCurrentBurstTime(self):
        return self.bursts[self.currBurstIndex]

class Simulator:
    def __init__(self, datfile, noOfCPUs=1, noOfIOs=1):
        self.datfile = datfile
        self.new = Queue()
        self.wait = Queue()
        self.ready = Queue()
        self.terminated = Queue()
        self.running = []
        for _ in range(noOfCPUs):
            self.running.append(CPU())
        self.IOs = []
        for _ in range(noOfIOs):
            self.IOs.append(IO())

        self.sleepTime = 1
        self.sysclock = SysClock()
        self.setupGUI()

        self.readData()

    def setupGUI(self):
        # New Queue Window 
        with dpg.window(label="New Queue", width=100, height=500, tag="newQueueWindow"):
            pass
        # Ready Queue Window
        with dpg.window(label="Ready Queue", width=100, height=500, pos=[100,0], tag="readyQueueWindow"):
            pass
        # Running Queue Window
        with dpg.window(label="Running Queue", width=100, height=500, pos=[200,0], tag="runningQueueWindow"):
            pass
        # Waiting Queue Window
        with dpg.window(label="Waiting Queue", width=100, height=500, pos=[300,0], tag="waitingQueueWindow"):
            pass
        # IO Queue window
        with dpg.window(label="IO Queue", width=100, height=500, pos=[400,0], tag="IOQueueWindow"):
            pass
        # Exit Queue window
        with dpg.window(label="Exit Queue", width=100, height=500, pos=[500,0], tag="exitQueueWindow"):
            pass
        # Message window
        with dpg.window(label="Current Status", width=200, height=200, pos=[600,0], tag="messageWindow"):
            dpg.add_text("FCFS Scheduling", tag="messageBox", wrap=200)
        # Final Message window
        with dpg.window(label="Result", width=200, height=300, pos=[600,200], tag="FinalMessageWindow"):
            pass

    def NewToReady(self):
        """ Move the process from new queue to ready queue by arrival time
        """
        while(len(self.new.queue) > 0):
            self.ready.addPCB(self.new.queue.pop())
            dpg.set_value("messageBox", f"At t:{self.sysclock.getClock()} job with pid: {self.ready.queue[-1].pid} entered Ready queue")

    def showTables(self):
        # new queue table
        with dpg.table(header_row=True, resizable=True, tag="newQueueTable", parent="newQueueWindow"):
            dpg.add_table_column(label="PID")
            dpg.add_table_column(label="Priority")
            for i in range(len(self.new.queue)):
                with dpg.table_row():
                    dpg.add_text(str(self.new.queue[i].pid))
                    dpg.add_text(str(self.new.queue[i].priority))
                
        # ready queue table
        with dpg.table(header_row=True, resizable=True, tag="readyQueueTable", parent="readyQueueWindow"):
            dpg.add_table_column(label="PID")
            dpg.add_table_column(label="Priority")    
            for i in range(len(self.ready.queue)):
                with dpg.table_row():
                    dpg.add_text(str(self.ready.queue[i].pid))
                    dpg.add_text(str(self.ready.queue[i].priority))

        # running queue table
        with dpg.table(header_row=True, resizable=True, tag="runningQueueTable", parent="runningQueueWindow"):
            dpg.add_table_column(label="PID")
            dpg.add_table_column(label="Priority")
            for cpu in self.running:
                if cpu.runningPCB:
                    with dpg.table_row():
                        dpg.add_text(str(cpu.runningPCB.pid))
                        dpg.add_text(str(cpu.runningPCB.priority))

        # waiting queue table
        with dpg.table(header_row=True, resizable=True, tag="waitingQueueTable", parent="waitingQueueWindow"):
            dpg.add_table_column(label="PID")
            dpg.add_table_column(label="Priority")
            for i in range(len(self.wait.queue)):
                with dpg.table_row():
                    dpg.add_text(str(self.wait.queue[i].pid))
                    dpg.add_text(str(self.wait.queue[i].priority))

        # IO queue table
        with dpg.table(header_row=True, resizable=True, tag="IOQueueTable", parent="IOQueueWindow"):
            dpg.add_table_column(label="PID")
            dpg.add_table_column(label="Priority")
            for i in range(len(self.IOs)):
                if self.IOs[i].servingPCB:
                    with dpg.table_row():
                        dpg.add_text(str(self.IOs[i].servingPCB.pid))
                        dpg.add_text(str(self.IOs[i].servingPCB.priority))
        
        # exit queue table
        with dpg.table(header_row=True, resizable=True, tag="exitQueueTable", parent="exitQueueWindow"):
            dpg.add_table_column(label="PID")
            dpg.add_table_column(label="Priority")
            for i in range(len(self.terminated.queue)):
                with dpg.table_row():
                    dpg.add_text(str(self.terminated.queue[i].pid))
                    dpg.add_text(str(self.terminated.queue[i].priority))

    def clearTables(self):
        dpg.delete_item("newQueueTable", children_only=False)
        dpg.delete_item("readyQueueTable", children_only=False)
        dpg.delete_item("runningQueueTable", children_only=False)
        dpg.delete_item("waitingQueueTable", children_only=False)
        dpg.delete_item("IOQueueTable", children_only=False)
        dpg.delete_item("exitQueueTable", children_only=False)

    def FCFS(self):
        """ First Come First Serve 
        """

        while len(self.ready.queue) > 0 or len(self.wait.queue) > 0 or len(self.new.queue) > 0 or any([cpu.runningPCB for cpu in self.running]) or any([io.servingPCB for io in self.IOs]):
            self.showTables()  
            self.NewToReady()
         

            if len(self.ready.queue) > 0: 
                for cpu in self.running:
                    if not cpu.busy:
                        cpu.loadProcess(self.ready.removePCB())
                        cpu.busy = True
                        dpg.set_value("messageBox", f"At t:{self.sysclock.getClock()} job {cpu.runningPCB.pid} obtained cpu:{self.running.index(cpu)}")
                    if len(self.ready.queue) <= 0:
                        break
                        
            for cpu in self.running:
                if cpu.runningPCB:
                    # decrement the current process
                    cpu.decrementCurrentProcess()
                    cpu.incrementExecutionTime()

                    finishedProcess = cpu.KickOff()
                    if finishedProcess:
                        finishedProcess.incrementBurstIndex()
                        if finishedProcess.currBurstIndex == len(finishedProcess.bursts):
                            self.terminated.addPCB(finishedProcess)
                            finishedProcess.TAT = self.sysclock.getClock() - finishedProcess.arrivalTime
                            dpg.add_text(f"At t:{self.sysclock.getClock()} Job {finishedProcess.pid} terminated: TAT = {finishedProcess.TAT}, Wait time = {finishedProcess.readyQueueTime}, I/O wait = {finishedProcess.waitQueueTime }", parent="FinalMessageWindow", wrap=200)
                        else:
                            finishedProcess.currBurst = 'IO'
                            self.wait.addPCB(finishedProcess)
                            dpg.set_value("messageBox", f"At t:{self.sysclock.getClock()} job {finishedProcess.pid} entered Waiting queue")


            # if there is a process in the wait queue
            if len(self.wait.queue) > 0:
                for io in self.IOs:
                    if not io.busy:
                        io.loadProcess(self.wait.removePCB())
                        io.busy = True
                        dpg.set_value("messageBox", f"At t:{self.sysclock.getClock()} job {io.servingPCB.pid} obtained device:{self.IOs.index(io)}")
                    if len(self.wait.queue) <= 0:
                        break

            for io in self.IOs:
                if io.servingPCB:
                    io.decrementCurrentProcess()
                    finishedProcess = io.KickOff()
                    if finishedProcess:
                        finishedProcess.incrementBurstIndex()
                        if finishedProcess.currBurstIndex == len(finishedProcess.bursts):
                            self.terminated.addPCB(finishedProcess)
                            finishedProcess.TAT = self.sysclock.getClock() - finishedProcess.arrivalTime
                            dpg.add_text(f"At t:{self.sysclock.getClock()} Job {finishedProcess.pid} terminated: TAT = {finishedProcess.TAT}, Wait time = {finishedProcess.readyQueueTime}, I/O wait = {finishedProcess.waitQueueTime }", parent="FinalMessageWindow", wrap=200)

                        else:
                            self.ready.addPCB(finishedProcess)
                            finishedProcess.currBurst = 'CPU'
                            dpg.set_value("messageBox", f"At t:{self.sysclock.getClock()} job:{finishedProcess.pid} IO finished, moved to READY state")
                            
            self.sysclock.increment()
            self.ready.incrememnt(what='runtime')
            self.wait.incrememnt(what='waittime')
            self.readData()
            dpg.render_dearpygui_frame()
            time.sleep(self.sleepTime)
            self.clearTables()
        self.showStat()

    def PB(self):   
        """ Priority Bases
        """
        while len(self.ready.queue) > 0 or len(self.wait.queue) > 0 or len(self.new.queue) > 0 or any([cpu.runningPCB for cpu in self.running]) or any([io.servingPCB for io in self.IOs]):
            self.showTables()
            preemted = False
            index = 0
            # move the process from new queue to ready queue by arrival time
            while index < len(self.new.queue):
                if self.new.queue[index].arrivalTime == self.sysclock.getClock():
                    self.ready.addPCB(self.new.queue[index])
                    self.new.queue.pop(index)
                    dpg.set_value("messageBox", "Process started with pid: " + str(self.ready.queue[-1].pid))

                    currentProcessPriority = int(self.ready.queue[-1].priority[1:])
                    
                    for cpu in self.running:
                        if cpu.runningPCB:
                            runningProcessPriority = int(cpu.runningPCB.priority[1:])
                            if currentProcessPriority > runningProcessPriority:
                                newProcess = self.ready.queue.pop()

                                # preempt the running process
                                self.ready.addPCB(cpu.runningPCB)
                                dpg.set_value("messageBox", f"Process {cpu.runningPCB.pid} preempted")
                                cpu.runningPCB = None
                                cpu.busy = False
                                preemted = True

                                # schedule the new process
                                cpu.loadProcess(newProcess)
                                cpu.busy = True
                                dpg.set_value("messageBox", f"Process {cpu.runningPCB.pid} scheduled to run")
                else:
                    index += 1

            if len(self.ready.queue) > 0: 
                for cpu in self.running:
                    if not cpu.busy:
                        # get the process with the heightest priority
                        processIndex = 0
                        maxPriority = int(self.ready.queue[0].priority[1:])
                        for i in range(len(self.ready.queue)):
                            if maxPriority < int(self.ready.queue[i].priority[1:]):
                                processIndex = i
                                maxPriority = int(self.ready.queue[i].priority[1:])

                        cpu.loadProcess(self.ready.queue.pop(processIndex))
                        cpu.busy = True
                        dpg.set_value("messageBox", f"Process {cpu.runningPCB.pid} scheduled to run")
                    if len(self.ready.queue) <= 0:
                        break
                        
            for cpu in self.running:
                if cpu.runningPCB:
                    # decrement the current process
                    cpu.decrementCurrentProcess()
                    cpu.incrementExecutionTime()
                    finishedProcess = cpu.KickOff()
                    if finishedProcess:
                        finishedProcess.incrementBurstIndex()
                        if finishedProcess.currBurstIndex == len(finishedProcess.bursts):
                            self.terminated.addPCB(finishedProcess)
                            finishedProcess.TAT = self.sysclock.getClock() - finishedProcess.arrivalTime
                            dpg.add_text(f"Job {finishedProcess.pid} terminated: TAT = {finishedProcess.TAT}, Wait time = {finishedProcess.readyQueueTime}, I/O wait = {finishedProcess.waitQueueTime }", parent="FinalMessageWindow", wrap=200)
                        else:
                            finishedProcess.currBurst = 'IO'
                            self.wait.addPCB(finishedProcess)
                            dpg.set_value("messageBox", f"Process {finishedProcess.pid} moved to WAITING state")

            # if there is a process in the wait queue
            if len(self.wait.queue) > 0:
                for io in self.IOs:
                    if not io.busy:
                        io.loadProcess(self.wait.removePCB())
                        io.busy = True
                        dpg.set_value("messageBox", "Starting IO request to process: " + str(io.servingPCB.pid))
                    if len(self.wait.queue) <= 0:
                        break

            for io in self.IOs:
                if io.servingPCB:
                    io.decrementCurrentProcess()
                    finishedProcess = io.KickOff()
                    if finishedProcess:
                        finishedProcess.incrementBurstIndex()
                        if finishedProcess.currBurstIndex == len(finishedProcess.bursts):
                            self.terminated.addPCB(finishedProcess)
                            finishedProcess.TAT = self.sysclock.getClock() - finishedProcess.arrivalTime
                            dpg.add_text(f"Job {finishedProcess.pid} terminated: TAT = {finishedProcess.TAT}, Wait time = {finishedProcess.readyQueueTime}, I/O wait = {finishedProcess.waitQueueTime }", parent="FinalMessageWindow", wrap=200)
                        else:
                            if preemted:
                                # add process returning from IO before the preempted process
                                preemtedProcess = self.ready.removePCB()
                                self.ready.addPCB(finishedProcess)
                                self.ready.addPCB(preemtedProcess)
                            else:
                                self.ready.addPCB(finishedProcess)
                            finishedProcess.currBurst = 'CPU'
                            dpg.set_value("messageBox", f"IO finished, Process {finishedProcess.pid} moved to READY state")
                            
            # increment the system clock
            self.sysclock.increment()
            self.ready.incrememnt(what='runtime')
            self.wait.incrememnt(what='waittime')
            self.readData()
            dpg.render_dearpygui_frame()
            time.sleep(self.sleepTime)
            self.clearTables()

        self.showStat()
        
    def RR(self, timeQuantum):
        """ Round Robin
        """
        while len(self.ready.queue) > 0 or len(self.wait.queue) > 0 or len(self.new.queue) > 0 or any([cpu.runningPCB for cpu in self.running]) or any([io.servingPCB for io in self.IOs]):
            preemted = False
            self.NewToReady()
            self.showTables()
            if len(self.ready.queue) > 0: 
                for cpu in self.running:
                    if not cpu.busy:
                        cpu.loadProcess(self.ready.removePCB())
                        cpu.busy = True
                        dpg.set_value("messageBox", f"Process {cpu.runningPCB.pid} scheduled to run")
                    if len(self.ready.queue) <= 0:
                        break
            
            for cpu in self.running:
                if cpu.runningPCB:
                    # decrement the current process
                    cpu.decrementCurrentProcess()
                    cpu.incrementExecutionTime()

                    finishedProcess = cpu.KickOff()
                    if finishedProcess:
                        finishedProcess.incrementBurstIndex()
                        if finishedProcess.currBurstIndex == len(finishedProcess.bursts):
                            self.terminated.addPCB(finishedProcess)
                            finishedProcess.TAT = self.sysclock.getClock() - finishedProcess.arrivalTime
                            dpg.add_text(f"Job {finishedProcess.pid} terminated: TAT = {finishedProcess.TAT}, Wait time = {finishedProcess.readyQueueTime}, I/O wait = {finishedProcess.waitQueueTime }",parent="FinalMessageWindow", wrap=200)
                        else:
                            finishedProcess.currBurst = 'IO'
                            self.wait.addPCB(finishedProcess)
                            dpg.set_value("messageBox", f"Process {finishedProcess.pid} moved to WAITING state")
                    else:
                        if cpu.executionTime % timeQuantum == 0:
                            # preempt the running process
                            self.ready.addPCB(cpu.runningPCB)
                            dpg.set_value("messageBox", f"Process {cpu.runningPCB.pid} preempted")
                            cpu.runningPCB = None
                            cpu.busy = False
                            preemted = True

            # if there is a process in the wait queue
            if len(self.wait.queue) > 0:
                for io in self.IOs:
                    if not io.busy:
                        io.loadProcess(self.wait.removePCB())
                        io.busy = True
                        dpg.set_value("messageBox", "Starting IO request to process: " + str(io.servingPCB.pid))
                    if len(self.wait.queue) <= 0:
                        break

            for io in self.IOs:
                if io.servingPCB:
                    io.decrementCurrentProcess()
                    finishedProcess = io.KickOff()
                    if finishedProcess:
                        finishedProcess.incrementBurstIndex()
                        if finishedProcess.currBurstIndex == len(finishedProcess.bursts):
                            self.terminated.addPCB(finishedProcess)
                            finishedProcess.TAT = self.sysclock.getClock() - finishedProcess.arrivalTime
                            dpg.add_text(f"Job {finishedProcess.pid} terminated: TAT = {finishedProcess.TAT}, Wait time = {finishedProcess.readyQueueTime}, I/O wait = {finishedProcess.waitQueueTime }", parent="FinalMessageWindow", wrap=200)
                        else:
                            if preemted:
                                # add process returning from IO before the preempted process
                                preemtedProcess = self.ready.removePCB()
                                self.ready.addPCB(finishedProcess)
                                self.ready.addPCB(preemtedProcess)
                            else:
                                self.ready.addPCB(finishedProcess)
                            finishedProcess.currBurst = 'CPU'
                            dpg.set_value("messageBox", f"IO finished, Process {finishedProcess.pid} moved to READY state")

            self.sysclock.increment()
            self.ready.incrememnt(what='runtime')
            self.wait.incrememnt(what='waittime')
            self.readData()
            dpg.render_dearpygui_frame()
            time.sleep(self.sleepTime)
            self.clearTables()

        self.showStat()

            
    def __str__(self):
        s = ""
        s += "datfile: "+self.datfile + "\n"
        s += "new queue: " + str(self.new) + "\n"
        s += "wait: "+",".join(str(self.wait)) + "\n"
        return s

    def readData(self):
        with open(self.datfile) as f:
            self.data = f.read().split("\n")

        for process in self.data:
            if len(process) > 0:
                parts = process.split(' ')
                arrival = parts[0]
                pid = parts[1]
                priority = parts[2]
                bursts = parts[3:]
                bursts = list(map(int, bursts))
                if self.sysclock.getClock() == int(arrival):
                    # create a PCB object
                    pcb = PCB(int(pid), bursts, int(arrival), priority)
                    self.new.addPCB(pcb)
                    dpg.set_value("messageBox", f"At t:{self.sysclock.getClock()} job with pid: {pid} entered new queue")

    def showStat(self):
        result_str = ""
        result_str += "CPU Utilization %: " + str(sum([cpu.executionTime for cpu in self.running])*100/(self.sysclock.getClock() * len(self.running))) + "\n"
        result_str += "Average Turnaround Time: " + str(sum([p.TAT for p in self.terminated.queue])/len(self.terminated.queue)) + "\n"
        result_str += "Average wait Time: " + str(sum([p.readyQueueTime for p in self.terminated.queue])/len(self.terminated.queue)) + "\n"
        result_str += "Average I/O wait Time: " + str(sum([p.waitQueueTime for p in self.terminated.queue])/len(self.terminated.queue)) + "\n"
        dpg.set_value("messageBox", result_str)


if __name__ == '__main__':
    
    if len(sys.argv) < 5:
        print("Usage: python3 Schedular.py <Scheduling Algorithm> <number of CPU> <number of IO> <input file> <Time Quantum-(Required for RR)>")
        print("""
            
            Scheduling Algorithm:
                FCFS: First Come First Serve
                PB: Priority Based
                RR: Round Robin""")
        sys.exit(1)
    if sys.argv[1] not in ['FCFS', 'PB', 'RR']:
        print("Invalid Scheduling Algorithm")
        sys.exit(1)
    if sys.argv[1] == "RR" and len(sys.argv) < 6:
        print("Time Quantum is required for RR")
        sys.exit(1)

    noOfCpus = int(sys.argv[2])
    noOfIOs = int(sys.argv[3])
    algo = sys.argv[1]
    inputFile = sys.argv[4]
    if algo == "RR":
        timeQuantum = sys.argv[5]

    sim = Simulator(inputFile, noOfCpus,noOfIOs)


    dpg.create_viewport(title='CPU Scheduling Simulation', width=800, height=500)
    dpg.setup_dearpygui()
    dpg.show_viewport()

    # run algo
    if algo == "FCFS":
        sim.FCFS()
    elif algo == "PB":
        sim.PB()
    elif algo == "RR":
        sim.RR(int(timeQuantum))

    dpg.start_dearpygui()
    
    
    # dpg.destroy_context()
