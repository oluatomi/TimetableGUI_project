
from PyQt5 import QtCore
from ..models.Tt_manager import TimeTableManager
from ..models import Tt_exceptions
import time


Author = "Oluwatomilayo Inioluwa OWOEYE"

class TtWorkerSignals(QtCore.QObject):
    """ The worker class to handle the "emmission" of signals to be caught by the progressbar in the GUI """
    finished = QtCore.pyqtSignal(str)
    # the Error string
    nil_error = QtCore.pyqtSignal(str)
    error = QtCore.pyqtSignal(str)
    progress = QtCore.pyqtSignal(int)
    # Runs at the end of the entire process, error or no
    deadend = QtCore.pyqtSignal()
    progress_with_info = QtCore.pyqtSignal(tuple)



class TtWorker(QtCore.QRunnable):
    """ GENERIC WORKER THREAD. The worker thread """
    def __init__(self, working_obj, finished_string="Operation complete", error_string="Error occured in the run",
        nil_error_string="Basic requirements not met", aux_function=None):
        super().__init__()
        self.signals = TtWorkerSignals()
        # The working object is the function/method passed in that will be run in the run function. Working_obj is a tuple
        # of the one (or two or more) threading operations that need to be carried out, (e.g, packeting and repacketing)
        # the auxiliary function (aux_function) is to be run when the nil_error_string is emitted

        self.working_obj = working_obj
        # Below.. the working object run with args and kwargs
        self.working_object = None
        self.auxiliary_object = aux_function

        self.finished_str = finished_string
        self.error_str = error_string
        self.nil_error_str = nil_error_string
        # Comment does not necessarily contain a string, it contains a list of objects (most likely strings), upon which notes would be developed
        # for display in the textEdit in the GUI
        self.comment = None


    def run_working_object(self, *args, **kwargs):
        """ run the working_object with whatever arguments and keyword arguments it might require.
        I'm intentionally not adding *args and kwargs as arguments to the run method. """
        self.working_object = self.working_obj(*args, **kwargs)



    @QtCore.pyqtSlot()
    def run(self):
        """ To emit signals... """

        operations = self.working_object if self.working_object else self.working_obj()

        if operations is None:
            if self.auxiliary_object:
                self.auxiliary_object()
            self.signals.nil_error.emit(self.nil_error_str)
            return


        for count, operation in enumerate(operations, start=1):
            loop, keep = True, True
            while loop:
                try:
                    beamed_val = next(operation)
                
                except StopIteration:
                    loop = False
                
                except Tt_exceptions.SomethingWentWrong as err:
                    # If an error occurs on repacketing, emit the error signal and completely break out of the for- and while- loops
                    self.comment = err.comment
                    loop, keep = False, False
                    self.signals.error.emit(self.error_str)

                else:
                    time.sleep(0.01)
                    self.signals.progress.emit(beamed_val)
            
            if not keep:
                # Break out of the wrapping for-loop if there is the SomethingWentWrong exception
                break
            # --- If this is the last_item emit the finished signal with the finished string
            if count == len(operations):
                self.signals.finished.emit(self.finished_str)

        # Emit a signal to signify that the run process has run fully, error or no
        self.signals.deadend.emit()


# -------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------
class WorkerForFrames(QtCore.QRunnable):
    """ TYPICALLY TO SEND DATA TO THE GUI WIDGETS FOR DISPLAY IN THE PERIOD FRAMES, and maybe something else more """
    def __init__(self, working_obj, finished_string="", error_string="", nil_error_string="Basic requirements not met", aux_function=None):
        super().__init__()
        self.signals = TtWorkerSignals()
        self.working_obj = working_obj
        # ---------------
        self.working_object = None
        # ---------------------
        self.finished_str = finished_string
        self.error_str = error_string
        self.nil_error_str = nil_error_string
        self.auxiliary_function = aux_function
        self.comment = None


    def run_working_object(self, *args, **kwargs):
        """ run the working_object with whatever arguments and keyword arguments it might require.
        I'm intentionally not adding *args and kwargs as arguments to the run method. """
        self.working_object = self.working_obj(*args, **kwargs)


    @QtCore.pyqtSlot()
    def run(self):
        """ To emit signals... """
        operations = self.working_object if self.working_object else self.working_obj()
        # -----------------------------------------------------------------------------------
        if operations is None:
            if self.auxiliary_object:
                self.auxiliary_object()
            self.signals.nil_error.emit(self.nil_error_str)
            return
        # -----------------------------------------------------------------------------------
        operations = operations if isinstance(operations, tuple) else (operations,)
        # print(f"THIS IS OPERATION 11 {operations}")    

        for count, operation in enumerate(operations, start=1):
            loop, keep = True, True

            # print(f"THIS IS OPERATION {operation}")
            
            while loop:
                try:
                    beamed_val, beamed_info = next(operation)

                    # print(f"beamed val and info {beamed_val, beamed_info}")

                except StopIteration:
                    loop = False
                    
                except Tt_exceptions.SomethingWentWrong as err:
                    # If an error occurs on repacketing, emit the error signal and completely break out of the for- and while- loops
                    self.comment = err.comment
                    loop, keep = False, False
                    self.signals.error.emit(self.error_str)

                else:
                    self.signals.progress.emit(beamed_val)
                    self.signals.progress_with_info.emit(beamed_info)
            if not keep:
                # Break out of the wrapping for-loop if there is the SomethingWentWrong exception
                break
            # --- If this is the last_item emit the finished signal with the finished string
            if count == len(operations):
                self.signals.finished.emit(self.finished_str)

        self.signals.deadend.emit()



