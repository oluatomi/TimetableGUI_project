# - ************************************************************************
# -- WRITTEN AND OWNED BY OWOEYE, OLUWATOMILAYO INIOLUWA. APRIL, 2022.
# -- All rights (whichever applies) reserved!
# **************************************************************************


# ---------------------------------------------------------------------------------
# --------------------- CODE FOR ALL THE EXCEPTIONS RAISED ------------------------
# ---------------------------------------------------------------------------------
class ProjectExceptions:

    class MyOwnException(Exception):
        def __init__(self, comment):
            super().__init__(comment)
            self.comment = comment


    class ClassAlreadyExists(MyOwnException):
        """For when your're making a class that already exists"""
        pass

    class NoTeacherAvailabale(MyOwnException):
        """for when a period assigns a teacher that doesn't exist from a dept"""
        pass

    class IsASpecialDept(MyOwnException):
         """For when teachers' info or class count or academic demands are made from
         a department (OR SUBJECT) that is not an academic dept, e.g break, 
         or xtra-curriculars"""
         pass

    class SubjectOrClassNotRegistered(MyOwnException):
        """When a period is instantiated without the school class or department (subject) registered,
         i.e. being in the list of departments or classes"""
        pass

    class CannotAssignFavPeriod(MyOwnException):
        pass

    class SubjectAlreadyExists(MyOwnException):
        """When a class that already exists is about to be re-instantiated"""
        pass

    class ClassArmCannotBeMade(MyOwnException):
        """ This happens when there is a problem making class arms because the num_id or the school class
        objects have not been supplied """
        pass

    class TeacherCannotBeAssigned(MyOwnException):
        """In the event when a teacher attempts to be assigned from a department's empty list (if auto),
         or tries to access a 'teacher_index' that doesn't exist"""
        pass

    class TeacherAlreadyGivenSaidSubject(MyOwnException):
        """ This alarm is raised if a teacher is assigned a subject which he had been previously assigned """
        pass

    class SomethingWentWrong(MyOwnException):
        """Used as a general exception class for displaying when something is wrong."""
        pass
