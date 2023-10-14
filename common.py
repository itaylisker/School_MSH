class Enum:
    LOGIN_INFO = 'login'
    ADD_SUBJECT = 'add_subject'
    GET_SUBJECTS = 'get_subjects'
    ADD_TEACHER = 'add_teacher'
    GET_TEACHERS = 'get_teachers'
    ADD_GRADE = 'add_grade'



# TODO: think of an encryption that isn't hash
def encode_password(password):
    import hashlib
    return hashlib.md5(password.encode()).hexdigest()
