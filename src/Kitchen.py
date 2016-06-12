"""
Kitchen is a main controller class of SOHOJUNG.
This class controls all the user events and drives business logic.
Model part of SOHOJUNG is called office.

author: Bak Hyeonjae
"""
import threading
import time
from threading import Timer
from copy import deepcopy
import Stack
import re
import sys
import const
import io

class Kitchen(threading.Thread):
   
    def __init__(self,mode,fileArg,cfgArg):
        threading.Thread.__init__(self)
        
        self.lifeLine = []
        self.callStack = [] #Stack.Stack()
        self.threads = []

        self.mode = mode
        self.argFile = fileArg
        self.cfgFile = cfgArg
        self.flag_capture_start = False
        self.flag_capture_stop = False
        self.cnt = 0

    def connectView(self,view):
        self.view = view    # set restaurant(view) component
        
    def connectToolBox(self,toolBox):
        self.toolBox = toolBox
    
    def run(self):

        print("kitchen --> start loading")

        #file_in = open("test_all.txt","r")

        self.lifeLine.append("start")
        self.view.addLifeline("start")

        input_dat = []

        if const.mode_interactive == self.mode:
            input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='ignore')
            for idx, line in enumerate(input_stream):
                if False == self.flag_capture_start:
                    continue
                if True == self.flag_capture_stop:
                    self.flag_capture_start = False
                    break
                input_dat.append(line)
        elif const.mode_batch == self.mode:
            input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='ignore')
            for idx, line in enumerate(input_stream):
                input_dat.append(line)
        elif const.mode_file == self.mode:
            file_in = open(self.argFile,"r", encoding='utf-8', errors='ignore')
            for idx, line in enumerate(file_in):
                input_dat.append(line)

        idx_for_remove = []
        for idx, line in list(reversed(list(enumerate(input_dat)))):
            match_flag = False
            if '[exit]' in line:
                for _i in reversed(range(0,idx)):
                    if '[entry]' in input_dat[_i]:
                        exit_str = line.split()
                        exit_method_name = ''
                        for _j in range(8,len(exit_str)):
                            exit_method_name += exit_str[_j]

                        entry_str = input_dat[_i].split()
                        entry_method_name = ''
                        for _j in range(8,len(entry_str)):
                            entry_method_name += entry_str[_j]

                        entry_method_name_arg_removed = entry_method_name.split("[args]")[0]
                        entry_method_name_arg_ret_removed = entry_method_name_arg_removed.split("[returns]")[0]
                        exit_method_name_arg_removed = exit_method_name.split("[args]")[0]
                        exit_method_name_arg_ret_removed = exit_method_name_arg_removed.split("[returns]")[0]

                        if entry_method_name_arg_ret_removed == exit_method_name_arg_ret_removed:
                            match_flag = True
                            break

                if False == match_flag:
                    print("REMOVE the line !!! -> %d" % idx)
                    print(line)
                    idx_for_remove.append(idx)

        for _i in idx_for_remove:
            del input_dat[_i]

        cfg_file_in = open(self.cfgFile,"r", encoding='utf-8', errors='ignore')
        
        cfg_time_index = 0
        cfg_thread_index = 0
        cfg_flowtype_index = 0
        cfg_methodname_index = 0
        cfg_ignore_str = None

        for line in cfg_file_in:
            if '[time]' in line:
                str = line.split('[time]')
                cfg_time_index = int(str[1])
            elif '[thread]' in line:
                str = line.split('[thread]')
                cfg_thread_index = int(str[1])
            elif '[flowtype]' in line:
                str = line.split('[flowtype]')
                cfg_flowtype_index = int(str[1])
            elif '[methodname]' in line:
                str = line.split('[methodname]')
                cfg_methodname_index = int(str[1])
            elif '[ignore]' in line:
                str = line.split('[ignore]')
                cfg_ignore_str = str[1].split(',')
        cfg_file_in.close()

        print("%d,%d,%d,%d" % (cfg_time_index,cfg_thread_index,cfg_flowtype_index,cfg_methodname_index))

        index = 0        
        for idx, line in enumerate(input_dat):
            if re.match("(.*)SHERLOCK/PROFILING(.*)",line):
                str_list = line.replace('static','').replace('synchronized','').replace('public','').replace('private','').replace('protected','').split()
                if len(str_list) < 9:
                    print("input line has some errors : %s"%line)
                    continue

                event_time = str_list[cfg_time_index]
                thread_id = str_list[cfg_thread_index]
                flow_type = str_list[cfg_flowtype_index]
                method_name_index = cfg_methodname_index

                package_method_name = ''
                for _i in range(method_name_index,len(str_list)):
                    package_method_name += str_list[_i]

                arguments_str = package_method_name.split("[args]")[1] if "[args]" in package_method_name else None
                return_str = package_method_name.split("[returns]")[1] if "[returns]" in package_method_name else None
                arg_removed = package_method_name.split("[args]")[0]
                ret_removed = arg_removed.split("[returns]")[0]
                parameter_removed = package_method_name.split("(")[0]
                method_name = list(reversed(parameter_removed .split(".")))[0]
                package_name = ".".join(list(reversed(list(reversed(parameter_removed .split(".")))[1:])))

                class_name = package_name

                if not (thread_id in self.threads):
                    self.threads.append(thread_id)
                    stack = Stack.Stack()
                    stack.push({'class':"start", 'message':""})
                    self.callStack.append(stack)

                if not (class_name in self.lifeLine):
                    self.view.addLifeline(class_name)
                    self.lifeLine.append(class_name)

                thread_index = self.threads.index(thread_id)

                if flow_type == "[entry]":
                    self.view.sendSignal(self.callStack[thread_index].peek(),class_name,method_name,thread_index,event_time,index+1,self.callStack[thread_index],arguments_str.split() if arguments_str else None)
                    self.callStack[thread_index].push({'class':class_name, 'message':method_name})

                if flow_type == "[exit]":
                    self.view.completeTask(class_name,method_name,1,event_time,index+1,self.callStack[thread_index].depth('compareClass'),return_str)
                    self.callStack[thread_index].pop()

                index += 1

            del line
            self.cnt = index

        print("kitchen --> refreshData")
        self.view.refreshData(self.cnt)
        self.view.setDrawingAvailable()
        self.toolBox.setAvailable(self.threads)
        print("kitchen start")
        
    def activateHide(self,flag):
        pass

    def resetAllLifelines(self):
        pass

    def activateCapture(self,flag):
        if False == self.flag_capture_start:
            self.flag_capture_start = True
        else:
            self.flag_capture_stop = True

    def searchMessage(self,str):
        pass

    def moveToPrev(self):
        pass
        
    def moveToNext(self):
        pass