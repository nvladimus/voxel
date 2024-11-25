# example usage
from enum import IntEnum, StrEnum

from voxel.utils.descriptors.enumerated import enumerated_property
from voxel.utils.descriptors.new.annotated import PropertyInfo


# Enumeration for StrEnum example
class StudentStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    GRADUATED = "graduated"


# Enumeration for IntEnum example
class StudentGrade(IntEnum):
    A = 4
    B = 3
    C = 2
    D = 1
    F = 0


# Enumeration for IntEnum with non-sequential values
class YearLevel(IntEnum):
    FRESHMAN = 1
    SOPHOMORE = 2
    JUNIOR = 3
    SENIOR = 4


# Custom dynamic options function that returns different valid options
def dynamic_student_level_options(obj) -> set[int]:
    return {YearLevel.FRESHMAN, YearLevel.SENIOR} if obj._status == StudentStatus.ACTIVE else {YearLevel.JUNIOR}


# Example class using EnumeratedProperty with both StrEnum, IntEnum, and dynamic options
class Student:
    def __init__(self):
        self._status = StudentStatus.ACTIVE
        self._grade = StudentGrade.A
        self._year_level = YearLevel.FRESHMAN

    # Using enumerated_property with StrEnum
    @enumerated_property(StudentStatus, PropertyInfo("", "Student status"))
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str):
        self._status = value

    # Using enumerated_property with IntEnum
    @enumerated_property(StudentGrade, PropertyInfo("", "Student grade"))
    def grade(self) -> int:
        return self._grade

    @grade.setter
    def grade(self, value: int):
        self._grade = value

    # Using dynamic options for the year level
    @enumerated_property(dynamic_student_level_options, PropertyInfo("", "Student year level"))
    def year_level(self) -> int:
        return self._year_level

    @year_level.setter
    def year_level(self, value: int):
        self._year_level = value

    # Notification mechanism for property updates
    def on_property_update_notice(self, msg: str, prop: str) -> None:
        print(f"Property: {prop} - {msg}")


# Instantiate the Student object
student = Student()

# Case 1: Accessing and updating StrEnum property (status)
print("Initial status:", student.status)  # Output: StudentStatus.ACTIVE
print("Available status options:", student.status.options)  # Output: {'active', 'graduated', 'inactive'}

# Try setting a valid status
student.status = StudentStatus.INACTIVE
print("Updated status:", student.status)  # Output: StudentStatus.INACTIVE

student.status = StudentStatus.GRADUATED
print("Updated status:", student.status)  # Output: StudentStatus.GRADUATED

student.status = StudentStatus.ACTIVE
print("Updated status:", student.status)  # Output: StudentStatus.ACTIVE

# Try setting an invalid status
student.status = "SUSPENDED"  # This will trigger the update notice

# Case 2: Accessing and updating IntEnum property (grade)
print("\nInitial grade:", student.grade)  # Output: StudentGrade.A
print("Available grade options:", student.grade.options)  # Output: {4, 3, 2, 1, 0}

# Try setting a valid grade
student.grade = StudentGrade.B
print("Updated grade:", student.grade)  # Output: StudentGrade.B

# Try setting an invalid grade
student.grade = 5  # This will trigger the update notice

# Case 3: Accessing and updating property with dynamic options (year level)
print("\nInitial year level:", student.year_level)  # Output: YearLevel.FRESHMAN
print("Available year level options (dynamic):", student.year_level.options)  # Output depends on student status

# Change status to see dynamic options change
student.status = StudentStatus.INACTIVE
print("Available year level options after status change:", student.year_level.options)  # Output changes dynamically

# Try setting a valid year level based on dynamic options
student.year_level = YearLevel.JUNIOR
print("Updated year level:", student.year_level)  # Output: YearLevel.JUNIOR

# Try setting an invalid year level based on dynamic options
student.year_level = YearLevel.SOPHOMORE  # This will trigger the update notice
